import re
import glob
import copy

from yaml import full_load_all

#TODO: Write function to put *** *** around unmatched tags and write out as a separate text file or write back to original interview file (dont know how to manage lines here)

#TODO: add parameter to limit lines to be processed for the interview or place line seperator characters in joined string that can be used to find the error with tags
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
 
 
    def readFramework(self):
        framework = self.readYaml()
        return framework
    
    
    def readInterviews(self):
        interviewList = []
        for interview in self.framework:
            
            # Get interview Text
            file = f'{self.projectLocation}/interviews/{interview["file"]}'
            interviewText = self.readInterview(file)            
                        
            interviewList.append(
                Interview(
                    file = file,
                    name = interview['interview'],
                    text = interviewText,
                    framework = interview['code framework'],      
                )
            )
        return interviewList
             
        
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
    def __init__(self, file, name, text, framework):
        self.file = file
        self.name = name
        self.framework = framework
        self.rawText = text
        
        matchedTags, unmatchedOpeningTags, unmatchedClosingTags = self.extractTags()
        
        self.tags = matchedTags
        self.unmatchedOpeningTags = unmatchedOpeningTags
        self.unmatchedClosingTags = unmatchedClosingTags
  
        self.codes = self.processCodes()
        
        
    def extractTags(self):
        openingTags, closingTags = self.findRawTags(
            interviewText = self.rawText,
            openingTagFilterStr='<[^/].+?>',
            closingTagFilterStr='</.+?>')
               
        matchedTags = {}
        unmatchedOpeningTags = []
        unmatchedClosingTags = []
        idx = 0
        openingTagCount = len(openingTags)
        while openingTags and closingTags:
            openingTag = openingTags.pop(0)
            match = self.matchTag(openingTag, closingTags)
            if match is not None:            
                closingTags, closingTag = match
                
                matchedTags = dictOfListsAppend(
                    dict = matchedTags,
                    key = openingTag.group(0)[1:-1],
                    val = (openingTag, closingTag))
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


    def convertTagsToText(self, tags):
        textTags = []
        for tagPair in tags:
            start = tagPair[0].span()[1]# end of first tag is start of text
            end = tagPair[1].span()[0]# start of first tag is end of text
            textTags.append(self.rawText[start:end])
        return textTags

  
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
                    tags = self.convertTagsToText(tags)
                )
            )
              
        return codes
     
     
#TODO: Maybe this should still be used??? just pass tags to codes, could add lots of logic neatly here
# 
# class Tag:
#     """
#     Data Class to store all tag information
#     """
#     def __init__(self, tag, startIdx, endIdx, rawText):
#         self.startIdx = startIdx
#         self.endIdx = endIdx
#         self.rawText = rawText
#         self.text = self.cleanRawText(rawText)
    
#     def cleanRawText(self, rawText):
#         text = re.sub('<.*?>', '', rawText)
#         return text
    
#     def __repr__(self):
#         return f'<{self.text}>'
    
    
    
class Code:
    def __init__(self, code, definition=None, tags=None):
        self.code = code
        self.definition = definition
        self.tags = tags
    
    
    def __repr__(self):
       return f'<{self.code}>'
       
             
        
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