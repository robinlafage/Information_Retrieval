import nltk.stem.porter as stem 

class Stemmer:
    def __init__(self,normalizeToLowerCase,tokens_list):
        self.normalizeToLowerCase = normalizeToLowerCase
        self.tokens_list = tokens_list

    def stemming(self):
        return [stem.PorterStemmer().stem(token, self.normalizeToLowerCase) for token in self.tokens_list]

if __name__ == "__main__" :
    stemmer = Stemmer(False, ["I", "show", "off", "of", "this"])
    tokens = stemmer.stemming()
    print(' '.join(tokens))