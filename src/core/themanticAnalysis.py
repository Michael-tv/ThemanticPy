import re
import glob
import copy
import os
from dataclasses import dataclass, make_dataclass, field
from typing import List, OrderedDict
from unicodedata import category

from yaml import full_load_all, dump_all

import networkx as nx


#! Next Steps

#TODO: add function that prints out all codes that have not been assigned to a category

#TODO: Start with network functions
    #TODO: network showing dag of theme
    #TODO: network showing codes, categories and themes to interviews 

#TODO: Write function to put *** *** around unmatched tags and write out as a separate text file or write back to original interview file (dont know how to manage lines here)

#TODO: add parameter to limit lines to be processed for the interview or place line seperator characters in joined string that can be used to find the error with tags
"""
Tag description
tag id is assigned automatically, in the background, just level needs to be specified

<id=001, tag=name, tone=P, comment=> stuff said in here </1>
Tone = N negative, P = positive, N = Neutral

"""

#TODO: Save tagged codes to code framework in model.yaml file!


class ThemanticAnalysis:
    def __init__(self, projectFile):

        self.interviews = []
        self.projectFile = projectFile
        self.project = []
        self.unusedCodesFramework = []
        self.interviews = []
        self.codeFramework = []
        self.unusedCodeFramework = []
        self.categoryFramework = []
        self.themeFramework = []
        
        projectData = self.readProjectData()
        # Break project data into constituent parts
        interviews = []
        for document in projectData:
            if 'project' in document.keys():
                self.project = document['project']
            elif 'interview' in document.keys():
                interviews.append(document['interview'])
            elif 'code framework' in document.keys():
                self.codeFramework = document['code framework']
            elif 'unused codes' in document.keys():
                self.unusedCodeFramework = document['unused codes']
            elif 'category framework' in document.keys():
                self.categoryFramework = document['category framework']
            elif 'theme framework' in document.keys():
                self.themeFramework = document['theme framework']
       
        self.codes = []
        self.categories = []
        self.themes = []
        self.unusedCodes = []
        
        self.interviews = self.readInterviews(interviews)

        self.processCodes()
        self.processCategories()
        self.processThemes()


    def processCodes(self):

        taggedCodes = self.readInterviewCodes()
        taggedCodeList = [code.code for code in taggedCodes]
          
        unusedCodes = {}
        #  Create a list of all codes to search though
        allCodes = self.codeFramework.copy()
        if len(self.unusedCodeFramework) > 0:
            allCodes.extend(
                [{key: val} for key, val in self.unusedCodeFramework.items()])
                 
        # Search through all codes
        for code in allCodes:   
            key, val = code.copy().popitem()          
            if key in taggedCodeList:
                
                #TODO check for duplicate tags

                # Combine definitions and codes for updated framework
                for frameworkCode in self.codeFramework:
                    key = list(frameworkCode.keys())[0]
                    val = list(frameworkCode.values())[0]
                    
                    # Search through tagged codes for key
                    for taggedCode in taggedCodes:                   
                        if key == taggedCode.code:
                            taggedCode.definition = val
            else:
                unusedCodes.update({key: val})

        self.codes = taggedCodes
        self.unusedCodes = unusedCodes
        
        
    def processCategories(self):
        for cat, info in self.categoryFramework.items():
            codeList = []
            if info is None:
                print(cat, info)
            if info['codes']:
                for item in info['codes']:
                    for code in self.codes:
                        if code.code == item:
                            codeList.append(code)
            
            # if len(self.categoryFramework[cat]['codes']) != len(codeList):
            #     raise Exception('not all codes matched')
                       
            self.categories.append(
                Category(
                    category = cat,
                    definition = self.categoryFramework[cat].get('description') , 
                    codeList = codeList
                )
            )
            
            
    def processThemes(self):
        
        for theme, info in self.themeFramework.items():    
            print(theme)
            catList = []
            if info['categories']:
                
                for item in info['categories']:
                    
                    for category in self.categories:
                        if category.category == item:
                            catList.append(category)
            
            # if len(self.themeFramework[cat]['categories']) != len(catList):
            #     raise Exception('not all categories matched')

            self.themes.append(
                Theme(
                    theme = theme,
                    definition = self.themeFramework[theme]['description'], 
                    categoryList = catList
                )
            ) 
      
        
    def readInterviewCodes(self):
        codes = []
        for interview in self.interviews:
            for tag in interview.tags:               
                if tag.tag in [code.code for code in codes]:
                    idx = [code.code for code in codes].index(tag.tag)
                    codes[idx].addTag(tag)# Add type check to tag adding element
                else:
                    codes.append(
                        Code(
                            code = tag.tag,
                            tags = tag,
                            interview = interview
                        )
                    )     
        return codes
    
    def buildProjectFile(self):
        projectFile = []
        
        # Project Section
        projectFile.append({'project': self.project})
        
        # Interviews Section
        for interview in self.interviews:
            projectFile.append({'interview': interview.serialize()})
            
        # Code Framework section
        serialCodes = []
        for code in self.codes:
            serialCodes.append(code.serialize())
        projectFile.append({'code framework': serialCodes})    
            
        # Unused Codes section    
        projectFile.append({'unused codes': self.unusedCodes})
        
        # Category frame work section
        projectFile.append({'category framework': self.categoryFramework})
            
        # Theme framework section
        projectFile.append({'theme framework': self.themeFramework})
            
        return projectFile
    

    def saveModel(self):
        #Rename current file to <model>.bq1        

        currentFilename = f'{self.projectFile}'
        
        # Get all Yaml files in folder
        modelFiles = []
        for file in glob.glob(f'{self.project["path"]}/{self.projectFile[:-1]}'):
            modelFiles.append(file)
        
        if len(modelFiles) >= 1:
            # Find latest backup filename
            backupNumbers = [int(x[-1]) for x in modelFiles]      
            
            # Save current file as new backup
            backupFileName = f'{currentFilename[:-1]}{max(backupNumbers) + 1}'
            os.rename(currentFilename, backupFileName)
    
        else:
            os.rename(currentFilename, currentFilename[:-3] + 'bq1')
    
        # Save new file
        with open(currentFilename, 'w') as file:
            dump_all(
                self.buildProjectFile(),
                file,
                default_flow_style=False
            )

    def readProjectData(self):
        projectData = self.readYaml(self.projectFile)
        return projectData
        
    
    def readInterviews(self, interviewList):               
        # Get interview Text
        interviews = []
        for interview in interviewList:  
            print(f'Reading interview: {interview["interview"]}')         
            file = f'{self.project["path"]}/{interview["file"]}'
            interviewText = self.readInterview(file)            
            interviews.append(
                Interview(
                    file = file,
                    name = interview['interview'],
                    info = interview,
                    text = interviewText
                )
            )
        return interviews
             
    def readInterview(self, file):
        with open(file, 'r') as fileObj:
            fileContent = fileObj.readlines()
        fileContentStr = ' '.join(fileContent)
        return fileContentStr  
        
    def readYaml(self, file):
        # Select first yaml file in project folder 
        
        #TODO: add try except clause here  
                
        with open(file) as f:
            file = full_load_all(f)
            projectData = []
            for doc in file:
                projectData.append(doc)
        return projectData
    
    
    def codesWithoutCategories(self, unassigned=True):
        
        assignedCodes = []
        for category in self.categories:
            assignedCodes.extend(category.codeList)
        
        #TODO: convert to set and back

        unassignedCodes = []
        for code in self.codes:
            if code not in assignedCodes:
                unassignedCodes.append(code)
 
        
        #TODO: convert to set and back
        
        if unassigned:
            return unassignedCodes
        else:
            return assignedCodes

    def extractAllNodes(self):
        # extract all nodes
        allNodes = []
        for theme in self.themes:
            for category in theme.categoryList:
                for code in category.codeList:
                    if code.code not in allNodes:
                        allNodes.append(code.get_code())
                if category.category not in allNodes:
                    allNodes.append(category.get_category())
            if theme.theme not in allNodes:
                allNodes.append(theme.get_theme())                  

        assignmentDict = {}
        for i, node in enumerate(allNodes):
            assignmentDict[node] = f'node_{i}'
        labelDict = {y: self.reformatLabel(x) for x, y in assignmentDict.items()}

        return allNodes
    
    def buildThemeNet(self, colors=None):
        
        if colors is None:
            colors = ['#4E79A7', '#F28E2B', '#E15759', '#76B7B2', '#59A14F', '#EDC948', '#B07AA1', '#FF9DA7', '#9C755F', '#BAB0AC']
        
        print('Starting node extraction', end='...')
        allNodes = self.extractAllNodes()
        print('Done')
        assignmentDict = {}
        for i, node in enumerate(allNodes):
            assignmentDict[node] = f'node_{i}'
        labelDict = {y: self.reformatLabel(x) for x, y in assignmentDict.items()}
        
        # networkList = []
        networkList = OrderedDict()
        for theme in self.themes:
            network = nx.Graph()
            # network = nx.DiGraph()
            labels = {}
            
            cIdx = 0
            assignedNodes = {}
            for category in theme.categoryList:
                network.add_node(assignmentDict[category.get_category()], nodeType='category', color=colors[-1])
                key = assignmentDict[category.get_category()]
                val = labelDict[key]
                labels[key] = val
                # network.add_edge(assignmentDict[theme.get_theme()], assignmentDict[category.get_category()])

                for code in category.codeList:
                    # breakpoint()
                    if code.interview.name not in assignedNodes.keys():
                        assignedNodes[code.interview.name] = colors[cIdx]
                        color = colors[cIdx]
                        cIdx += 1
                    else:
                        color = assignedNodes[code.interview.name]
                    
                    network.add_node(code.interview.name.replace(' ', '_'), nodeType='interview', color=color)
                    labels[code.interview.name.replace(' ', '_')] = code.interview.name
                    network.add_edge(assignmentDict[category.get_category()], code.interview.name.replace(' ', '_'), color=color)
            
            networkList[theme.get_theme()] = (network, labels)
        
        return networkList
    
    
    def buildInterviewNet(self):
        allNodes = self.extractAllNodes()
        assignmentDict = {}
        for i, node in enumerate(allNodes):
            assignmentDict[node] = f'node_{i}'
        labelDict = {y: self.reformatLabel(x) for x, y in assignmentDict.items()}

        interviewNet = {}
        for interview in self.interviews:
            network = nx.DiGraph()
            labels = {}
            for theme in self.themes:
                for category in theme.categoryList:
                    for code in category.codeList:
                        if code.interview == interview:
                            # Add Code
                            network.add_node(assignmentDict[code.get_code()], nodeType='code')
                            key = assignmentDict[code.get_code()]
                            labels[key] = labelDict[key]  
                            
                            # Add Category
                            network.add_node(assignmentDict[category.get_category()], nodeType='category')
                            key = assignmentDict[category.get_category()]
                            labels[key] = labelDict[key]  
                            
                            # Add Theme                          
                            network.add_node(assignmentDict[theme.get_theme()], nodeType='theme')
                            key = assignmentDict[theme.get_theme()]
                            labels[key] = labelDict[key]  
                                                        
                            # Add Edges
                            network.add_edge(
                                assignmentDict[code.get_code()],
                                assignmentDict[category.get_category()])
                            network.add_edge(
                                assignmentDict[category.get_category()],
                                assignmentDict[theme.get_theme()])
            interviewNet[interview.name] = (network, labels)

        return interviewNet
    

    def reformatLabel(self, name, lineLength=15):
        words = name[4:].split(' ')
        length = 0
        newName = []
        for idx, word in enumerate(words):
            length += len(word)
            if length >= lineLength:
                newName.append('\n')
                length = 0
            newName.append(word)
        return ' '.join(newName)

    def buildDataFrameworkNet(self):
        # extract all nodes
        allNodes = self.extractAllNodes()

        assignmentDict = {}
        for i, node in enumerate(allNodes):
            assignmentDict[node] = f'node_{i}'
        labelDict = {y: self.reformatLabel(x) for x, y in assignmentDict.items()}

        networkList = []
        for theme in self.themes:
            network = nx.DiGraph()
            labels = {}
            network.add_node(assignmentDict[theme.get_theme()], nodeType='theme')
            key = assignmentDict[theme.get_theme()]
            val = labelDict[key]
            labels[key] = val

            for category in theme.categoryList:
                network.add_node(assignmentDict[category.get_category()], nodeType='category')
                key = assignmentDict[category.get_category()]
                val = labelDict[key]
                labels[key] = val
                network.add_edge(assignmentDict[theme.get_theme()], assignmentDict[category.get_category()])
                for code in category.codeList:
                    network.add_node(assignmentDict[code.get_code()], nodeType='code', interview=code.interview.name)
                    key = assignmentDict[code.get_code()]
                    val = labelDict[key]
                    labels[key] = val
                    network.add_edge(assignmentDict[category.get_category()], assignmentDict[code.get_code()], interview=code.interview.name)

            networkList.append((network, labels))

        return networkList

class Interview:
    def __init__(self, name, file, info, text):
        self.name = name
        self.file = file
        self.info = info
        self.rawText = text
                
        matchedTags, unmatchedOpeningTags, unmatchedClosingTags = self.extractTags()
        self.tags = matchedTags
        self.unmatchedOpeningTags = unmatchedOpeningTags
        self.unmatchedClosingTags = unmatchedClosingTags
          
        
    def extractTags(self):
        # Find all tags
        openingTags, closingTags = self.findRawTags(
            interviewText = self.rawText,
            openingTagFilterStr='<[^/].+?>',
            closingTagFilterStr='</.+?>')
        
        # Match Tags       
        matchedTags = []
        unmatchedOpeningTags = []
        unmatchedClosingTags = []
        idx = 0
        openingTagCount = len(openingTags)
        while openingTags and closingTags:
            openingTag = openingTags.pop(0)
            match = self.matchTag(openingTag, closingTags)
            if match is not None:                           
                closingTags, closingTag = match
                
                # Define matched Tag
                matchedTags.append(
                    Tag(
                        interviewName = self.name,
                        interviewRawText = self.rawText,
                        openingTag = openingTag,
                        closingTag = closingTag
                    )
                )                 
            else:
                print(f'UNMATCHED: tag Number {idx} of {openingTagCount}: {openingTag}')
                unmatchedOpeningTags.append(openingTag)
            idx += 1
        
        # Add remaining tags to unmatched list
        unmatchedClosingTags.extend(unmatchedClosingTags)       
        
        return matchedTags, unmatchedOpeningTags, unmatchedClosingTags    
    
    
    def findRawTags(self, openingTagFilterStr, closingTagFilterStr, interviewText):
        openingTags = list(re.finditer(openingTagFilterStr, interviewText))
        closingTags = list(re.finditer(closingTagFilterStr, interviewText))
        return openingTags, closingTags  
    
    
    def matchTag(self, openingTag, closingTags):
            
        openingTagName = self.extractTagText(
            pat = '<[^/].+?[|>]',
            text = openingTag.group(0),
            idxs = (1,-1)).strip()
        
        openingTag.group(0)[1:-1]
       
        openingTagId = self.extractTagText(
            pat = 'id[" "]*=[" "]*(.*?)[" "]*>',    
            text = openingTag.group(0),
            idxs = (1,-1))
        
        # Find first tag with matching name and id
        idx = 0
        closingTags = closingTags[:]
        while (len(closingTags) > 0) and (idx < len(closingTags)):
            
            closingTag = closingTags[idx]
            
            closingTagName = self.extractTagText(
                pat =  '</.+?[|>]',
                text = closingTag.group(0),
                idxs = (2,-1)).strip()
            
            closingTagId = self.extractTagText(
                pat =  'id[" "]*=[" "]*(.*?)[" "]*>',
                text = closingTag.group(0),
                idxs = (2,-1))
            
            if (openingTagName == closingTagName) & (closingTagId == openingTagId):
                closingTags.pop(idx)
                return closingTags, closingTag
            else:
                idx += 1  
            
    
    def extractTagText(self, pat, text, idxs=None):
        result = re.search(pat, text, re.IGNORECASE)   
        if result is not None:
            result = result.group(0)
            if idxs is not None:
                return result[idxs[0]:idxs[1]]
            else:
                return result
       
            
    def serialize(self):
        
        # Build dictionary from available info
        serialInterview = {
            'interview': self.name,
            'file': self.file}
            
        for key, val in self.info.items():
            serialInterview[key] = val

        return serialInterview
    
    
    def __repr__(self):
        return f'<{self.name}>'
     


class Tag:
    """
    Data Class to store all tag information
    """
    def __init__(self, interviewName, interviewRawText, openingTag, closingTag):
        self.startIdx = openingTag.end()
        self.endIdx = closingTag.start()
        openingTagName = openingTag.group(0)[1:-1]
        closingTagName = closingTag.group(0)[2:-1]
        
        if openingTagName == closingTagName:
            self.tag = openingTagName
        else:
            raise Exception('Opening Tag and Closing Tag does not match')
        
        self.interviewName = interviewName
        
        rawText = interviewRawText[self.startIdx:self.endIdx]
        self.text = self.cleanRawText(rawText)
    
    
    def cleanRawText(self, rawText):
        text = re.sub('<.*?>', '', rawText)
        return text
    
    def __repr__(self):
        return f'<TAG: {self.text}>'
    
    
class Code:
    def __init__(self, code, definition=None, tags=None, interview=None):
        self.code = code
        self.definition = definition
        self.interview = interview
        
        if type(tags) == list:        
            self.tags = tags
        else:
            self.tags = [tags]

    def get_code(self):
        return f'cod-{self.code}'

    def addTag(self, tag):
        self.tags.append(tag)

    def serialize(self):
        if self.definition != '':
            definition = self.definition
        else:
            definition = ''        
        return {self.code: definition}
    
    def __repr__(self):
       return f'<CODE: {self.interview} - {self.code}: {self.definition}>'
       
       
class Category:
    def __init__(self, category, definition=None, codeList=None):
        self.category = category
        self.definition = definition
        self.codeList = codeList
        
    def get_category(self):
        return f'cat-{self.category}'

    # def __repr__(self):
    #    return f'<CODE: {self.interview} - {self.code}: {self.definition}>'
       
             
# @dataclass        
# class Category:
#     category: str
#     definition: str = None
#     codeList: List[Code] = field(default_factory=List)




# @dataclass
# class Theme:
#     theme: str
#     definition: str = None
#     categoryList: List[Category] = field(default_factory=List)
    
#     def __repr__(self):
#         return f'<Theme - {self.theme}>'
    
class Theme:
    def __init__(self, theme, definition=None, categoryList=None):
        self.theme = theme
        self.definition = definition
        self.categoryList = categoryList
        
    def get_theme(self):
        return f'the-{self.theme}'

    # def __repr__(self):
    #    return f'<CODE: {self.interview} - {self.code}: {self.definition}>'

def dictOfListsAppend(dict, key, val):
    appendedDict = copy.deepcopy(dict)
    if appendedDict.get(key):#  Check if key exists
        if type(appendedDict[key]) is not list:# Check if value is a list ir a value
            appendedDict[key] = [appendedDict[key], val]
            return appendedDict
        else:
            appendedDict[key].append(val)
            return appendedDict
    else:
        appendedDict[key] = [val]    
        return appendedDict