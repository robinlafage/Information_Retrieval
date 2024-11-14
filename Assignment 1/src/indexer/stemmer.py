import nltk.stem.porter as stemmerLibrary

class Stemmer:
    def __init__(self,tokenList):
        self.tokenList = tokenList

    def stem(self):
        """
        Function that takes a list of string in order to stem each token of the list.

        Returns:
            [[string, string]]: A list of list which contains the original token and the token after stemming
        """
        tokenListAfterStemming = []
        for token in self.tokenList :
            #We never let the stemmer option to normalize to lower
            #If the token is only composed of digits, there is no need to stem it
            if not token.isdigit():
                tokenAfterStemming = stemmerLibrary.PorterStemmer().stem(token, False)
            else :
                tokenAfterStemming = token
            tokenListAfterStemming.append([token, tokenAfterStemming])
        return tokenListAfterStemming