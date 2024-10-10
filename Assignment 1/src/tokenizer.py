from stemmer import *

class Tokenizer:
    def __init__(self, string, minimumTokenLength, normalizeToLowerCase, cuttingListPath, stopWordsPath):
        self.string = string
        self.minimumTokenLength = minimumTokenLength
        self.normalizeToLowerCase = normalizeToLowerCase
        self.cuttingListPath = cuttingListPath
        self.stopWordsPath = stopWordsPath
        #StopWords won't work if we don't set the lowercase before checking if it's in the StopWords list

    def tokenize(self):
        token = ""
        tokenList = []  

        try :
            stopWordsFilePointer = open(self.stopWordsPath)
            stopWordsFile = stopWordsFilePointer.read()
            stopWords = stopWordsFile.split()
        except :
            stopWords = []

        try :
            cuttingListFile = open(self.cuttingListPath)
            cuttingList = cuttingListFile.read()
        except : 
            cuttingList = " "
        
        for i, character in enumerate(self.string) :  
            if character not in cuttingList :
                token = token + character
            elif i + 1 < len(self.string) and character in ".-" : 
                if self.string[i+1] and not self.string[i+1] in cuttingList :
                    pass
            elif token in stopWords :
                token = ""
            elif len(token) < self.minimumTokenLength :
                    token = ""
            else : 
                if self.normalizeToLowerCase :
                    token = token.lower()
                    if token in stopWords :
                        token = ""
                if token != "" :
                    tokenList.append(token)
                    token=""
        if token != "" \
           and len(token) > self.minimumTokenLength\
           and token not in stopWords:
            tokenList.append(token)

        #TODO Delete the prints
        print(tokenList)
        return tokenList

if __name__ == "__main__" :
    normalizeToLowerCase = True
    tokenizer = Tokenizer("Organizati\non U.S.A. of the genes encoding complement receptors type 1 and 2, decay-accelerating factor, and C4-binding protein in the RCA locus on human chromosome 1.\n\nThe organization and physical linkage of four members of a major complement locus, the RCA locus, have been determined using the technique of pulsed field gradient gel electrophoresis in conjunction with Southern blotting. The genes encoding CR1, CR2, DAF, and C4bp were aligned in that order within a region of 750 kb. In addition, the 5' to 3' orientation of the CR1 gene (5' proximal to CR2) was determined using 5'- and 3'-specific DNA probes. The proximity of these genes may be related to structural and functional homologies of the protein products. Overall, a restriction map including 1,500 kb of DNA was prepared, and this map will be important for positioning of additional coding sequences within this region on the long arm of chromosome 1.", \
                            3,\
                            normalizeToLowerCase,\
                            "../cuttingList.txt",\
                            "../stopwords-en.txt")
    tokens = tokenizer.tokenize()
    stemmer = Stemmer(normalizeToLowerCase, tokens)
    print(str(stemmer.stemming()))
    