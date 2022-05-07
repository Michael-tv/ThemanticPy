import re
import glob
import copy

from yaml import full_load_all


#! Next Steps

#TODO: Write functions to update model based on work done in analysis

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
    def __init__(self, projectLocation):
        """
        process
         - read file(s)
         - id tags
        
        _summary_

        Parameters
        ----------
        dictOfFiles : dictionary of all files to be included in analysis
            {descriptive name: path to file}
        """

        self.interviews = []
        self.projectLocation = projectLocation

        projectData = self.readProjectData()
        # Break project data into constituent parts
        interviews = []
        for document in projectData:
            if 'project' in document.keys():
                self.project = document
            elif 'interview' in document.keys():
                interviews.append(document)
            elif 'code framework' in document.keys():
                self.codeFramework = document
            elif 'category framework' in document.keys():
                self.categoryFramework = document
            elif 'theme framework' in document.keys():
                self.themeFramework = document 
       
        self.codes = []
        self.unusedCodes = []
        self.interviews = self.readInterviews(interviews)

        self.updateCodeFramework()


    def updateCodeFramework(self):
        
        taggedCodes = self.readInterviewCodes()
        
        taggedCodeList = [code.code for code in taggedCodes]
        
        # get codes from code framework and unused codes
        frameworkCodeDict = self.codeFramework.get('code framework')
        unusedCodeDict = self.codeFramework.get('unused codes')
        
        unusedCodes = {}
        if frameworkCodeDict != None:
            if unusedCodeDict != None:
                frameworkCodeDict.update(unusedCodeDict)
            
            for code, info in frameworkCodeDict.items():
                if code in taggedCodeList:
                    idx = taggedCodeList.index(code)
                    taggedCodes[idx].updateCodeInfo(info)
                else:
                    unusedCodes.update({code: info})
      
        self.codes = taggedCodes
        self.unusedCodes = unusedCodes
      
        
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
                            tags = tag
                        )
                    )     
        return codes

                    
            
        
        #TODO: split sections header, framework etc. 
         
        #TODO: for all tags
            #TODO: if tag in model, leave
            #TODO: if tag not in model, add
            #TODO: remaining tags, move to old tag framework for manual deletion
        
        #TODO: Join sections
        
        #TODO: Write yaml file

    
 
    def readProjectData(self):
        projectData = self.readYaml()
        return projectData
    
    
    def readInterviews(self, interviewList):               
        # Get interview Text
        interviews = []
        for interview in interviewList:
            file = f'{self.projectLocation}/interviews/{interview["file"]}'
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
        
        
    def readYaml(self):
        # Select first yaml file in project folder
        projectYaml = glob.glob(self.projectLocation + '/' + '*.yml')[0]
                
        with open(projectYaml) as f:
            file = full_load_all(f)
            projectData = []
            for doc in file:
                projectData.append(doc)
        return projectData


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
        matchedTags = []#{}
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
                print(f'tag Number {idx} of {openingTagCount}')
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
    def __init__(self, code, definition='', tags=None):
        self.code = code
        self.definition = definition
        
        if type(tags) == list:        
            self.tags = tags
        else:
            self.tags = [tags]


    def addTag(self, tag):
        self.tags.append(tag)


    def updateCodeInfo(self, codeInfo):    
        self.definition = codeInfo.get('definition')

    
    def __repr__(self):
       return f'<CODE: {self.code}: {self.definition}>'
       
             
        
class Category:
    def __init__(self, category, definition=None):
        self.category = category
        self.definition = definition
        self.codes = []



class Theme:
    def __init__(self, theme, definition=None):
        self.category = theme
        self.definition = definition
        self.categories = []


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