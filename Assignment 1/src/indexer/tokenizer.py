class Tokenizer:
    def __init__(self, stringToTokenize, minimumTokenLength, normalizeToLowerCase, allowedCharactersPath, stopWordsPath):
        self.stringToTokenize = stringToTokenize
        self.minimumTokenLength = minimumTokenLength
        self.normalizeToLowerCase = normalizeToLowerCase
        self.allowedCharactersPath = allowedCharactersPath
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
            allowedCharactersFile = open(self.allowedCharactersPath)
            allowedCharacters = allowedCharactersFile.read()
        except : 
            allowedCharacters = "abcdefghijklmnopqrstuvwxyz"
        
        #Usage of enumarate to have an index on the string, in order to check next character
        for i, character in enumerate(self.stringToTokenize) : 

            #If the character is an allowed character, we add it to the token and go to next iteration of the loop 
            if character.lower() in allowedCharacters :
                token = token + character

            
            #Since now, the character is NOT an authorized character

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
            if self.normalizeToLowerCase :
                token=token.lower()
            tokenList.append(token)

        return tokenList