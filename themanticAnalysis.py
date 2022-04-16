from collections import deque
import re
import glob
import copy

#TODO: remove tags from rawText in tags, do function in side tag to do this 


from yaml import full_load_all

"""
Tag description
tag id is assigned automatically, in the background, just level needs to be specified

<id=001, tag=name, tone=P, comment=> stuff said in here </1>
Tone = N negative, P = positive, N = Neutral

"""
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
        self.framework = self.readFramework() 
        self.interviews = self.readInterviews()
 

        #self.model = self.extractData()


    # def extractData(self):
        
    #     #TODO: Create tree structure of all data, codes, categories, themes
        
    #     # Generate Codes
        
        
    #     #TODO: Could also do this by looping over all known tags in framework
        
    #     # Extract all tags
    #     allTags = []
    #     for interview in self.interviews:
    #         allTags.extend(interview.tags)
        
    #     # Create set of all tags
    #     #TODO: Create function that creates new list or appends if list exists
    #     setAllTags = {}
    #     for tag in allTags:
    #         if setAllTags.get(tag.tag):
    #             setAllTags[tag.tag].append(tag)
    #         else:
    #             setAllTags[tag.tag] = [tag]
        
    #     codes = []
    #     for codeName in setAllTags:
    #         codes.append(
    #             Code(
    #                 code = codeName,
    #             )
    #         )
        
    #     breakpoint()
        
    #     model = []
        
    #     # This can be a network
        
    #     return model


    def readFramework(self):
        framework = self.readYaml()
        return framework
    
    
    def readInterviews(self):
        interviewList = []
        for interview in self.framework:
            
            # Get interview Text
            file = f'{self.projectLocation}/interviews/{interview["file"]}'
            interviewText = self.readInterview(file)

            # Extract interview Codes            
            openingTags, closingTags =  self.findRawTags(
                interviewText = interviewText,
                openingTagFilterStr='<{1}[^/<]+>{1}',
                closingTagFilterStr='</{1}[^<>]+>{1}'
            )   
            tags = self.getTags(openingTags, closingTags, interviewText)                
                        
            interviewList.append(
                Interview(
                    file = file,
                    name = interview['interview'],
                    text = interviewText,
                    framework = interview['code framework'], 
                    tags = tags                  
                )
            )
        return interviewList


    def findRawTags(self, openingTagFilterStr, closingTagFilterStr, interviewText):
        openingTags = list(re.finditer(openingTagFilterStr, interviewText))
        closingTags = list(re.finditer(closingTagFilterStr, interviewText))
        
        if len(openingTags) == len(closingTags):                
            return openingTags, closingTags
        else:
            raise Exception('Amount of opening tags should equal amount of closing tags')  
                

    def getTags(self, openingTags, closingTags, interviewText):
        
        openingTags = deque(openingTags)
        
        # Find matching opening and closing tags
        tags = {}
        while openingTags:
            openTag = openingTags.popleft()
            
            tagId = re.search(
                'id[" "]{0,10}=[" "]{0,10}(.*?)[" "]{0,10},',
                openTag.group(0),
                re.IGNORECASE) 

            # If no Id is assigned, assume closing tag is next tag 
            if tagId is None:
                closeTag = closingTags.pop(0) 

            # If tag id has been defined, find first closing tag with matching id
            else:
                for idx, closeTag in enumerate(closingTags):
                    closeId = re.search(
                        '<[" "]{0,10}/[" "]{0,10}(.*?)[" "]{0,10}>',
                        openTag.group(0),
                        re.IGNORECASE)
                    
                    if closeId == tagId:
                        closeTag = closingTags.pop(idx)
            
            tagObj = Tag(
                tag = openTag.group(0)[1:-1],
                startIdx = openTag.end(),
                endIdx = closeTag.end(),
                rawText = interviewText[openTag.start():closeTag.end()]
            )
            tags = dictOfListsAppend(
                dict = tags,
                key = openTag.group(0)[1:-1],
                val = tagObj
            )  
                
        return tags # [{'tag': {description: 'code definition', 'tagged text': text that has been tagged}}]    
        
        
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
    def __init__(self, file, name, text, framework, tags):
        self.file = file
        self.name = name
        self.framework = framework
        self.rawText = text
        self.tags = tags
  
        self.codes = self.processCodes()
  
    def processCodes(self):
        
        # Master list of codes, combined from interview text and framework
        listOfCodes = set(list(self.framework.keys()) + list(self.tags.keys()))
        codes = []
        for code in listOfCodes:           
            # Get code properties
            
            if self.framework.get(code):
                definition = self.framework[code]['code definition'] 
            else:
                definition = None
            
            if self.tags.get(code) is not None:
                tags = self.tags[code]
            else:
                tags = [] 
            
            codes.append(
                Code(
                    code = code,
                    definition = definition,
                    tags = tags
                )
            )
              
        return codes
    
    # def processTags(self, modelCodes, textCodes):
        
    #     for code in modelCodes:
            
    #         # Extract text codes
    #         codeStrings = []
    #         for item in textCodes:
    #             if item['tag'] == code:
    #                 codeStrings.append(item)

    #         # Create code
    #         testing = Tag(
    #             description = modelCodes['definition'],
    #             definition = modelCodes[''],
    #             startIds = 1,
    #             endIdx = 1,
    #         )
    
    #     return 
        
        
class Tag:
    """
    Data Class to store all tag information
    """
    def __init__(self, tag, startIdx, endIdx, rawText):
        self.startIdx = startIdx
        self.endIdx = endIdx
        self.rawText = rawText
        self.text = self.cleanRawText(rawText)
    
    def cleanRawText(self, rawText):
        text = re.sub('<.*?>', '', rawText)
        return text
    
    def __repr__(self):
        return f'<{self.text}>'
    
    
class Code:
    def __init__(self, code, definition=None, tags=None):
        self.code = code
        self.definition = definition
        self.tags = tags
    
    def __repr__(self):
       return self.code
             
        
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

#==============================================================================#       

if __name__ == '__main__': 
    
    projectLocation = 'C:/Users/michael.victor/Dropbox/interview project'

    analysis = ThemanticAnalysis(projectLocation)
    
    
    
    

# TODO: next steps in analysing links and relationships between interviewers and assigned tags        

"""
see following links for data analysis
https://datavizcatalogue.com/index.html_
https://datavizcatalogue.com/methods/wordcloud.html
https://datavizcatalogue.com/methods/parallel_coordinates.html
https://datavizcatalogue.com/methods/radar_chart.html

check relationships between team size, experience, industry, etc

"""