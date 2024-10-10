import nltk.stem.porter as stemmerLibrary

class Stemmer:
    def __init__(self,normalizeToLowerCase,tokenList):
        self.normalizeToLowerCase = normalizeToLowerCase
        self.tokenList = tokenList

    def stem(self):
        return [stemmerLibrary.PorterStemmer().stem(token, self.normalizeToLowerCase) for token in self.tokenList]

if __name__ == "__main__" :
    stemmer = Stemmer(False, ["I", "show", "off", "of", "this"])
    tokens = stemmer.stemming()
    print(' '.join(tokens))