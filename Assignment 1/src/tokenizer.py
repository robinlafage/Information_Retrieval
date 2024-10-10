from stemmer import *

class Tokenizer:
    def __init__(self, stringToTokenize, minimumTokenLength, normalizeToLowerCase, cuttingCharactersPath, stopWordsPath, useStemming):
        self.stringToTokenize = stringToTokenize
        self.minimumTokenLength = minimumTokenLength
        self.normalizeToLowerCase = normalizeToLowerCase
        self.cuttingCharactersPath = cuttingCharactersPath
        self.stopWordsPath = stopWordsPath
        #StopWords won't work if we don't set the lowercase before checking if it's in the StopWords list
        self.useStemming = useStemming

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
            cuttingCharactersFile = open(self.cuttingCharactersPath)
            cuttingCharacters = cuttingCharactersFile.read()
        except : 
            cuttingCharacters = " "
        
        for i, character in enumerate(self.stringToTokenize) :  
            if character not in cuttingCharacters :
                token = token + character
            elif i + 1 < len(self.stringToTokenize) and character in ".-" : 
                if self.stringToTokenize[i+1] and not self.stringToTokenize[i+1] in cuttingCharacters :
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

        if self.useStemming :
            stemmer = Stemmer(normalizeToLowerCase, tokenList)
            tokenList = stemmer.stem()
        return tokenList

if __name__ == "__main__" :
    stringToTokenize = "Organization of the genes encoding complement receptors type 1 and 2, decay-accelerating factor, and C4-binding protein in the RCA locus on human chromosome 1.\n\nThe organization and physical linkage of four members of a major complement locus, the RCA locus, have been determined using the technique of pulsed field gradient gel electrophoresis in conjunction with Southern blotting. The genes encoding CR1, CR2, DAF, and C4bp were aligned in that order within a region of 750 kb. In addition, the 5' to 3' orientation of the CR1 gene (5' proximal to CR2) was determined using 5'- and 3'-specific DNA probes. The proximity of these genes may be related to structural and functional homologies of the protein products. Overall, a restriction map including 1,500 kb of DNA was prepared, and this map will be important for positioning of additional coding sequences within this region on the long arm of chromosome 1."
    normalizeToLowerCase = True
    minimumTokenLength = 3
    cuttingCharactersPath="../cuttingCharacters.txt"
    stopwordsPath = "../stopwords-en.txt"
    useStemmer = True
    tokenizer = Tokenizer(stringToTokenize, 
                            minimumTokenLength,
                            normalizeToLowerCase,
                            cuttingCharactersPath,
                            stopwordsPath,
                            useStemmer)
    tokens = tokenizer.tokenize()
    if useStemmer :
        stemmer = Stemmer(normalizeToLowerCase, tokens)
    