#We can use every type of stemmer
#Kstem or Porter are best algo
#Dictionary based is slower, but could be better if the dictionary is good enough

class Stemmer:
    def __init__(self, token):
        self.token = token

