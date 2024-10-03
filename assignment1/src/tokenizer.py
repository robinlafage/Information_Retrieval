import re

class Tokenizer:
    def __init__(self, string, minimumTokenLength, cuttingList, stopWords):
        self.string = string
        self.minimumTokenLength = minimumTokenLength
        self.cuttingList = cuttingList
        self.stopWords = stopWords

    def tokenize(self):
        index = 0
        token = ""
        tokenList = []
        for character in self.string :  
            if character not in self.cuttingList :
                token = token + character
            #TODO Implement special rules for characters in cuttingList 
            #Exemple : "pique-nique" should be 1 or 2 tokens ?
            #Exemple : "Jhon's" should be 1 or 2 tokens ? If 2 tokens, "'s" should be "is" or "'s" ?
            elif token in self.stopWords :
                token = ""
            elif len(token) < self.minimumTokenLength :
                    token = ""
            else : 
                tokenList.append(token)
                token=""
        if token != "" and len(token) > self.minimumTokenLength:
            tokenList.append(token)

        print(tokenList)
        return tokenList

if __name__ == "__main__" :
    tokenizer = Tokenizer("Organization of the genes encoding complement receptors type 1 and 2, decay-accelerating factor, and C4-binding protein in the RCA locus on human chromosome 1.\n\nThe organization and physical linkage of four members of a major complement locus, the RCA locus, have been determined using the technique of pulsed field gradient gel electrophoresis in conjunction with Southern blotting. The genes encoding CR1, CR2, DAF, and C4bp were aligned in that order within a region of 750 kb. In addition, the 5' to 3' orientation of the CR1 gene (5' proximal to CR2) was determined using 5'- and 3'-specific DNA probes. The proximity of these genes may be related to structural and functional homologies of the protein products. Overall, a restriction map including 1,500 kb of DNA was prepared, and this map will be important for positioning of additional coding sequences within this region on the long arm of chromosome 1.", \
                            3, \
                            " .,;\'\"-_`@~\\/?!()[]\{\}"\
                            ["or","the"])
    tokenizer.tokenize()