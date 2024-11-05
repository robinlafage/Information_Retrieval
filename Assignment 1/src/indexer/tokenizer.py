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
            tokenList.append(token)

        return tokenList

if __name__ == "__main__" :
    stringToTokenize = "ff fffff fff[Vitalizing public health activities through community assessment: A report of the Committee on Public Health Nursing 2014-2017].\n\nObjectives\u3000This report aims to present the community assessment model developed by the Committee on Public Health Nursing (6th term) of the Japanese Association of Public Health. This new model was designed such that it could be applied to a broad range of public health activities. It aims at theorizing public health nurses' practice-based knowledge and sharing it among other public health professionals.Methods\u3000The model was developed during seven committee meetings held from October 2014 to September 2017. In the first step, we brainstormed the definition and methods of community assessment and constructed a framework for a literature review. In the second step, information on theories, research, and practice relevant to community assessment was reviewed based on this framework. In the third step, the community assessment model was developed based on the results of the literature review and the practice experience of the committee members. In the last step, we examined the applicability of this model to the practice of occupational health and public health administration.Project activities\u3000We defined community assessment as the \"skills and methods based on applied science that drive Plan-Do-Check-Action (PDCA) cycles in every activity that aims at achieving a better quality of life (QOL).\" We further classified community assessment into two types; comprehensive assessment and targeted assessment. The model underlined that community assessment was a continuous and developmental process that occurs throughout every stage of the PDCA cycle, and that it was oriented toward improving the QOL of community residents. This model also purported that the empirical and scientific intuition, and ethical sensitivity of assessors were among the key determinants of assessment quality.Conclusion\u3000The model on community assessment developed in the present study based on the empirical knowledge of public health nurses could be applied to all types of public health activities in communities."
    normalizeToLowerCase = False
    minimumTokenLength = 3
    allowedCharactersPath="../cuttingWordsV2.txt"
    stopwordsPath = "../stopwords-en.txt"
    tokenizer = Tokenizer(stringToTokenize, 
                            minimumTokenLength,
                            normalizeToLowerCase,
                            allowedCharactersPath,
                            stopwordsPath)
    tokens = tokenizer.tokenize()
    print(str(tokens))
    