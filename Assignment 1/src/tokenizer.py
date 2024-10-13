class Tokenizer:
    def __init__(self, stringToTokenize, minimumTokenLength, normalizeToLowerCase, cuttingCharactersPath, stopWordsPath):
        self.stringToTokenize = stringToTokenize
        self.minimumTokenLength = minimumTokenLength
        self.normalizeToLowerCase = normalizeToLowerCase
        self.cuttingCharactersPath = cuttingCharactersPath
        self.stopWordsPath = stopWordsPath
    
    def tokenize(self):
        """Function to create tokens from a given string

        Returns:
            [string]: A list of every tokens created
        """
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
        
        #Usage of enumarate to have an index on the string, in order to check next character
        for i, character in enumerate(self.stringToTokenize) : 

            #If the character is not a cutting character, we add it to the token and go to next iteration of the loop 
            if character not in cuttingCharacters :
                token = token + character
            
            #Exception rule : if it's a compound word (ex mother-in-law), we decide it's one token only (motherinlaw)
            #Exception rule : if a dot is directly followed by another character (ex U.S.A.), we decide it's one token only (USA)
            elif i + 1 < len(self.stringToTokenize) and character in ".-" : 
                if self.stringToTokenize[i+1] and not self.stringToTokenize[i+1] in cuttingCharacters :
                    pass

            
            #Since now, the character is a cutting character

            #If the token is in the stopwords list we delete the token 
            #As the list is only in lower, we have to check the lower form of the token, even if normalizeToLower is False
            elif token.lower() in stopWords :
                token = ""

            #If the token is shorter than the minimum token length we delete the token
            elif len(token) < self.minimumTokenLength :
                    token = ""

            else : 
                if self.normalizeToLowerCase :
                    token = token.lower()

                #If the token isn't empty, we add it to our list of tokens
                if token != "" :
                    tokenList.append(token)
                    token=""
        
        #If we finished the loop with a non empty token, longer or equal to the minimum token length, not a stopword
        #Then we can add it to our token list
        if token != "" \
           and not len(token) < self.minimumTokenLength\
           and token not in stopWords:
            tokenList.append(token)

        return tokenList

if __name__ == "__main__" :
    stringToTokenize = "Organization of the VeRY genes encoding complement receptors type 1 and 2, decay-accelerating factor, and C4-binding protein in the RCA locus on human chromosome 1.\n\nThe organization and physical linkage of four members of a major complement locus, the RCA locus, have been determined using the technique of pulsed field gradient gel electrophoresis in conjunction with Southern blotting. The genes encoding CR1, CR2, DAF, and C4bp were aligned in that order within a region of 750 kb. In addition, the 5' to 3' orientation of the CR1 gene (5' proximal to CR2) was determined using 5'- and 3'-specific DNA probes. The proximity of these genes may be related to structural and functional homologies of the protein products. Overall, a restriction map including 1,500 kb of DNA was prepared, and this map will be important for positioning of additional coding sequences within this region on the long arm of chromosome 1."
    normalizeToLowerCase = False
    minimumTokenLength = 3
    cuttingCharactersPath="../cuttingCharacters.txt"
    stopwordsPath = "../stopwords-en.txt"
    tokenizer = Tokenizer(stringToTokenize, 
                            minimumTokenLength,
                            normalizeToLowerCase,
                            cuttingCharactersPath,
                            stopwordsPath)
    tokens = tokenizer.tokenize()
    print(str(tokens))
    