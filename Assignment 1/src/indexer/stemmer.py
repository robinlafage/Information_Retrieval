import nltk.stem.porter as stemmerLibrary

class Stemmer:
    def __init__(self,tokenList):
        self.tokenList = tokenList

    def stem(self):
        tokenListAfterStemming = []
        for token in self.tokenList :
            #We never let the stemmer option to normalize to lower, always the work of tokenizer
            #If the token is only composed of digits, there is no need to stem it
            if not token.isdigit():
                tokenAfterStemming = stemmerLibrary.PorterStemmer().stem(token, False)
            else :
                tokenAfterStemming = token
            tokenListAfterStemming.append([token, tokenAfterStemming])
        return tokenListAfterStemming

if __name__ == "__main__" :
    stemmer = Stemmer(["I", "showed", "these", "off", "of", "this"])
    tokens = stemmer.stem()
    print(str(tokens))