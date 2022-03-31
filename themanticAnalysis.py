from collections import deque
import re

"""
Tag description
<id=001, tag=name, tone=P, comment=> stuff said in here </1>
Tone = N negative, P = positive, N = Neutral
    
    
"""


class ThemanticAnalysis:
    def __init__(self, dictOfFiles):
        """
        _summary_

        Parameters
        ----------
        dictOfFiles : dictionary of all files to be included in analysis
            {descriptive name: path to file}
        """
        
        self.filePath = dictOfFiles
        
    def readFile(filePath):    
    
        return
    
    
    def findTags(file):    
        
        # Find starts and ends of tags
        tagStartIdx = [{x.group()[4:7]:[x.start()]} for x in re.finditer('<id....', file)]     
        tagEndIdx = [{x.group()[2:6]:[x.start()]} for x in re.finditer('</...>', file)]
        # Check that there are equal amount of open and close tags
        
        assert (len(tagStartIdx) != len(tagEndIdx)), 'Number of opening tags must match number of closing tags' 
        
        
        #for tag in tagsIdx:
            
            
        
        # Iterate though all tags to find matching parts using a stack
        
        return tagStartIdx, tagEndIdx
        
        
# Process:
## Find all tags
# -> Find index of all opening tags
# -> FInd index of all corresponding closing tags
# -> Append (opening index, Closing Index) to tags list


# Run a function to check that all tags are unique
def findTagLocations(file):    
        
    # Find starts and ends of tags    
    # tagsStartIdx = [{x.group()[4:7]:x.start()} for x in re.finditer('<id....', file)]     
    tagsStartIdx = {x.group()[4:7]: x.start() for x in re.finditer('<id....', file)}
    tagsEndIdx = {x.group()[2:5]: x.start() for x in re.finditer('</...>', file)}
    
    # Check that there are equal amount of open and close tags
    test = len(tagsStartIdx) == len(tagsEndIdx)
    assert (test), 'Number of opening tags must match number of closing tags' 
    
    # tagsIdx = {} 
    # for key, _ in tagsStartIdx.items():
    #      tagsIdx[key, (tagsStartIdx[key], tagsEndIdx[key])]
     
    tagsIdx = {key:(tagsStartIdx[key], tagsEndIdx[key]) for key, val in tagsStartIdx.items()} 
     
    return tagsIdx

# def groupTags(tagStartIdx, tagEndIdx):
    
#     tagsIdx = 
#     for key, val in tagStartIdx:
        
#     return tagsIdx


if __name__ == '__main__': 
    
    
    file = 'transcription.txt'
    
    with open(file, 'r') as fileObj:
        file = fileObj.readlines()
        
    flatFile = ' '.join(file)
    
    # tagStartIdx = re.finditer('<id....', flatFile)    
    # tagsIdx = [{x.group()[4:7]:[x.start()]} for x in tagStartIdx ]
    
    # Only excepts single string, not a list e.g, flat file
    idx = findTagLocations(flatFile)
        
    
# TODO: next steps in analysing links and relationships between interviewers and assigned tags        

"""
see following links for data analysis
https://datavizcatalogue.com/index.html_
https://datavizcatalogue.com/methods/wordcloud.html
https://datavizcatalogue.com/methods/parallel_coordinates.html
https://datavizcatalogue.com/methods/radar_chart.html

check relationships between team size, experience, industry, etc

"""