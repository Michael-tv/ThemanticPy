from collections import deque
import re
import glob
from collections import deque

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
 

        self.model = self.extractData()

    def extractData(self):
        
        #TODO: Create tree structure of all data, codes, categories, themes
        
        # This can be a network
        
        return model

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
        tags = []
        
        while openingTags:
            openTag = openingTags.popleft()
            
            tagId = re.search(
                'id[" "]{0,10}=[" "]{0,10}(.*?)[" "]{0,10},',
                openTag.group(0),
                re.IGNORECASE) 

            # If no Id is assigned, assume closing tag is next tag 
            if tagId is None:
                closeTag = closingTags.pop(0)                   
                tags.append(
                    Tag(
                        tag = openTag.group(0)[1:-1],
                        startIdx = openTag.end(),
                        endIdx = closeTag.end(),
                        rawText = interviewText[openTag.start():closeTag.end()]
                    )
                )

            # If tag id has been defined, find first closing tag with matching id
            else:
                for idx, closeTag in enumerate(closingTags):
                    closeId = re.search(
                        '<[" "]{0,10}/[" "]{0,10}(.*?)[" "]{0,10}>',
                        openTag.group(0),
                        re.IGNORECASE)
                    
                    if closeId == tagId:
                        closeTag = closingTags.pop(idx)
                    
                tags.append(
                    Tag(
                        tag = openTag.group(0)[1:-1],
                        startIdx = openTag.end(),
                        endIdx = closeTag.end(),
                        rawText = interviewText[openTag.start():closeTag.end()]
                    )
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
  
  
    #TODO: function that creates codes from tags and framework 
    def createCodes(self):
        
        return
    
    def processTags(self, modelCodes, textCodes):
        
        for code in modelCodes:
            
            # Extract text codes
            codeStrings = []
            for item in textCodes:
                if item['tag'] == code:
                    codeStrings.append(item)

            # Create code
            testing = Tag(
                description = modelCodes['definition'],
                definition = modelCodes[''],
                startIds = 1,
                endIdx = 1,
            )
    
        return 
    
    # def allTags(self):
    #     allTags = {}
    #     for tagObj in self.tags:                      
    #         for tag in tagObj.tagList:
                
    #             #breakpoint()
                
    #             if tag in allTags.keys():
    #                 allTags[tag].append(tagObj.text)
    #             else:
    #                 allTags[tag] = [tagObj.text]
    #     return allTags
    
    
class Tag:
    """
    Data Class to store all tag information
    """
    def __init__(self, tag, startIdx, endIdx, rawText):
        self.tag = tag
        self.startIdx = startIdx
        self.endIdx = endIdx
        self.rawTextList = rawText
    
    def __repr__(self):
        return f'<{self.tag}>'
    

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