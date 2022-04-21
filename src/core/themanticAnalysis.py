import re
import glob
import copy

from yaml import full_load_all

#TODO: Write function to put *** *** around unmatched tags and write out as a separate text file or write back to original interview file (dont know how to manage lines here)


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
            openingTagFilterStr='<{1}[^/<]+>{1}',
            closingTagFilterStr='</{1}[^<>]+>{1}')
        
        matchedTags = {}
        unmatchedOpeningTags = []
        unmatchedClosingTags = []
        while openingTags and closingTags:
            openingTag = openingTags.pop(0)
            match = self.matchTag(openingTag, closingTags)
            if match is not None:            
                closingTagIdx, closingTag = match
                closingTags.pop(closingTagIdx)
                
                matchedTags = dictOfListsAppend(
                    dict = matchedTags,
                    key = openingTag.group(0)[1:-1],
                    val = (openingTag, closingTag))
                #matchedTags.append((openingTag, closingTag))
            else:
                unmatchedOpeningTags.append(openingTag)
        
        # Add remaining tags to unmatched list
        unmatchedOpeningTags.extend(unmatchedOpeningTags)
        unmatchedClosingTags.extend(unmatchedClosingTags)       
        
        return matchedTags, unmatchedOpeningTags, unmatchedClosingTags    
    
    
    def findRawTags(self, openingTagFilterStr, closingTagFilterStr, interviewText):
        openingTags = list(re.finditer(openingTagFilterStr, interviewText))
        closingTags = list(re.finditer(closingTagFilterStr, interviewText))
        return openingTags, closingTags  
    
    
    def matchTag(self, openingTag, closingTags):
        openingTagName = openingTag.group(0)[1:-1]  
       
        openingTagId = self.extractTagText(
            pat = 'id[" "]{0,10}=[" "]{0,10}(.*?)[" "]{0,10},',
            text = openingTag.group(0),
            idxs = (1,-1))
        
        # Find first tag with matching name and id
        for idx, closingTag in enumerate(closingTags):
            
            closingTagName = self.extractTagText(
                pat =  f'</{openingTagName}>',
                text = closingTag.group(0),
                idxs = (2,-1))         
            
            closingTagId = self.extractTagText(
                pat =  'id[" "]{0,10}=[" "]{0,10}(.*?)[" "]{0,10},',
                text = closingTag.group(0),
                idxs = (2,-1))    
                            
            if (openingTagName == closingTagName) & (closingTagId == openingTagId):
                return idx, closingTag
    
    
    def extractTagText(self, pat, text, idxs=None):
        result = re.search(pat, text, re.IGNORECASE)         
        if result is not None:
            result = result.group(0)
            if idxs is not None:
                return result[idxs[0]:idxs[1]]
            else:
                return result

  
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
