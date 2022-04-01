from collections import deque
import re
import glob

"""
Tag description
tag id is assigned automatically, in the background, just level needs to be specified

<id=001, tag=name, tone=P, comment=> stuff said in here </1>
Tone = N negative, P = positive, N = Neutral

# Process:
## Find all tags
# -> Find index of all opening tags
# -> FInd index of all corresponding closing tags
# -> Append (opening index, Closing Index) to tags list    
    
"""

#TODO: create a tag class to store all tag data

class Tag:
    def __init__(self, level=None):
        
        self.level = level
        
        # Write function that parses opening tag
        
        # Write function that parses closing tag
    
    def readOpeningTag():
        return
    
    def readClosingTag():        
        return

def findTags(str):
    openingTags = list(re.finditer('(<[^/][^<]+>)', str))
    closingTags = list(re.finditer('(</..>)', str))
    return openingTags, closingTags

    # Extract tag levels

def extractTagLevels():
    
    # Find all 
    
    return


def findHighestTagLevel(openingTags, closingTags):
    
    maxOpening = 0
    findStr = 'level='
    for tag in openingTags:
        tagStr = tag.group() 
        start = tagStr.find(findStr) + len(findStr) + 1
        end = start + 1
        level = tagStr[start:end]
        
        if maxOpening < int(level):
            maxOpening = int(level)
        
    maxClosing = 0
    findStr = '</'        
    for tag in closingTags:
        tagStr = tag.group()
        start = tagStr.find(findStr) + len(findStr) + 1
        end = start + 1
        level = tagStr[start:end]
        
        if maxClosing < int(level):
            maxClosing = int(level)
                   
    # check that maxOpeningLevel == maxClosingLevel
    assert (maxClosing == maxOpening), 'Max opening tag level must equal max closing tag level'
    
    return maxOpening 

def assignTagIds():
    
    
    
    return

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
        self.interviewData = self.readFiles()
            
    
    def readFiles(self):
                      
        # Read all files, assign filename as key
        files = {}
        for file in self.fileList:
                
            # Extract filename
            fileName = file.split('/')[-1][:-4]
                
            # Read file
            with open(file, 'r') as fileObj:
                fileContent = fileObj.readlines()
                
            #TODO Some filecleaning is reaquired here, strip ending spaces etc...
            fileContentStr = ' '.join(fileContent)  
                    
            files[fileName] = fileContentStr 

        self.interviewData = files   
        
    
    def findTagLocations(self):    
            
        # Find starts and ends of tags       
        tagsStartIdx = {x.group()[4:7]: x.start() for x in re.finditer('<id....', file)}
        tagsEndIdx = {x.group()[2:5]: x.start() for x in re.finditer('</...>', file)}
        
        # Check that there are equal amount of open and close tags
        test = len(tagsStartIdx) == len(tagsEndIdx)
        assert (test), 'Number of opening tags must match number of closing tags' 
        
        tagsIdx = {key:(tagsStartIdx[key], tagsEndIdx[key]) for key, val in tagsStartIdx.items()} 
        
        return tagsIdx
        

if __name__ == '__main__': 
    #C:\Users\michael.victor\Dropbox\Transcription
    fileList = ['C:/Users/michael.victor/Dropbox/Transcription/transcription.txt']
    
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