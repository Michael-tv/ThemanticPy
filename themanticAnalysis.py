from collections import deque
import re
import glob

"""
Tag description
<id=001, tag=name, tone=P, comment=> stuff said in here </1>
Tone = N negative, P = positive, N = Neutral

# Process:
## Find all tags
# -> Find index of all opening tags
# -> FInd index of all corresponding closing tags
# -> Append (opening index, Closing Index) to tags list    
    
"""
class ThemanticAnalysis:
    def __init__(self, fileList):
        """
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
    
    
    def findTagLocations(file):    
            
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