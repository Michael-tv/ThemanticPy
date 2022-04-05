from collections import deque
from logging import exception
import re
import glob

from collections import deque

"""
Tag description
tag id is assigned automatically, in the background, just level needs to be specified

<id=001, tag=name, tone=P, comment=> stuff said in here </1>
Tone = N negative, P = positive, N = Neutral

"""

class Tag:
    """
    Data Class to store all tag information
    """
    def __init__(self, startIdx, endIdx, rawText):
        self.startIdx = startIdx
        self.endIdx = endIdx
        self.rawText = rawText
        self.tagList = self.extractTagList()
        self.text = self.extractTagStr()

        return

    def extractTagList(self):
        
        try:        
            tagList = re.search(
                'tags\s*=\s*\\[(.*?)\s*\\]',
                self.rawText,
                re.IGNORECASE).group(1).split(',')
        except:
            raise Exception('No list of tags could be identified for tag')

        return tagList

    def extractTagStr(self):
        
        try:
        
            tagStrMatches = re.findall('>(.*?)</',
                    self.rawText,
                    re.IGNORECASE)
            
            # Find longest tag string
            tagStr = max(tagStrMatches)           
            return tagStr

        except:
            raise Exception('Cannot find tag string')
    
    def __repr__(self):
        return f'<{", ".join(self.tagList)}>'
    

class Interview:
    def __init__(self, name, text):
        self.name = name
        self.rawText = text
        self.tags = self.extractTags()
        
    def findRawTags(self):
        openingTags = list(re.finditer('(<[^/][^<]+>)', self.rawText))
        closingTags = list(re.finditer('(</..>)', self.rawText))
        return openingTags, closingTags   
        
    def extractTags(self):
        
        openingTags, closingTags = self.findRawTags()
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
                        startIdx = openTag.end(),
                        endIdx = closeTag.end(),
                        rawText = self.rawText[openTag.start():closeTag.end()]
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
                        startIdx = openTag.start(),
                        endIdx = closeTag.end(),
                        rawText = self.rawText[openTag.Start():closeTag.end()]
                    )
                )  
        return tags
    
    def allTags(self):
        allTags = {}
        for tagObj in self.tags:                      
            for tag in tagObj.tagList:
                
                #breakpoint()
                
                if tag in allTags.keys():
                    allTags[tag].append(tagObj.text)
                else:
                    allTags[tag] = [tagObj.text]
        return allTags
    
    
class ThemanticAnalysis:
    def __init__(self, fileList):
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
        
        self.fileList = fileList # Path to files that must be analysed
        self.interviews = self.readFiles()        
               
               
    # def processInterviewData(self):
    
    #TODO: convienience function that runs entire analysis
        
    #     files = self.readFiles()
        
    #     tagsIdx = self.findTagLocations(self)
        
        
    #     findTags(file)
        
    #     return interviewdata        
    
    def readFiles(self):
                      
        # Read all files, assign filename as key
        interviews = []
        for file in self.fileList:
                
            # Extract filename
            fileName = file.split('/')[-1][:-4]
                
            # Read file
            with open(file, 'r') as fileObj:
                fileContent = fileObj.readlines()
                
            #TODO Some filecleaning is reaquired here, strip ending spaces etc...
            fileContentStr = ' '.join(fileContent)  
            
            interviews.append(
                Interview(
                  name = fileName,
                  text = fileContentStr  
                )
            )

        return interviews
    
        

if __name__ == '__main__': 
    #C:\Users\michael.victor\Dropbox\Transcription
    fileList = ['C:/Users/michael.victor/Dropbox/Transcription/test_interview.txt']
    
    analysis = ThemanticAnalysis(fileList)
    
    

# TODO: next steps in analysing links and relationships between interviewers and assigned tags        

"""
see following links for data analysis
https://datavizcatalogue.com/index.html_
https://datavizcatalogue.com/methods/wordcloud.html
https://datavizcatalogue.com/methods/parallel_coordinates.html
https://datavizcatalogue.com/methods/radar_chart.html

check relationships between team size, experience, industry, etc

"""