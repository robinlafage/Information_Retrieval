import nltk.stem.porter as stemmerLibrary

class Stemmer:
    def __init__(self,normalizeToLowerCase,tokens_list):
        self.normalizeToLowerCase = normalizeToLowerCase
        self.tokens_list = tokens_list

    def stem(self):
        return [stemmerLibrary.PorterStemmer().stem(token, self.normalizeToLowerCase) for token in self.tokens_list]

if __name__ == "__main__" :
    stemmer = Stemmer(False, ["I", "show", "off", "of", "this"])
    tokens = stemmer.stemming()
    print(' '.join(tokens))