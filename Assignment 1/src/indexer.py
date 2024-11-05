from parser import *
from tokenizer import *
from stemmer import *
from merger import *
import json

class Indexer:
    def __init__(self, inputFile, outputFile, tokenizerOptions, stemmerOptions):
        self.inputFile = inputFile
        self.outputFile = outputFile
        self.tokenizerOptions = tokenizerOptions
        self.stemmerOptions = stemmerOptions
        self.tempDict = {}
        self.tempDictAfterStemming = {}
        self.outputDirectory = "../tmpIndexes"

    def buildIndex(self):
        self.buildPartialsIndexes()
        merger = Merger(self.inputFile, self.outputFile, self.tokenizerOptions, self.stemmerOptions)
        merger.merge()


    def buildPartialsIndexes(self):
        blocSize = 10000
        i = 0
        currentBloc = 0

        parser = Parser(None)
        tokenizer = Tokenizer(None, 
                              self.tokenizerOptions["minimumTokenLength"], 
                              self.tokenizerOptions["normalizeToLower"], 
                              self.tokenizerOptions["allowedCharactersFile"], 
                              self.tokenizerOptions["stopwordsFile"])
        if self.stemmerOptions["stemming"] :
            stemmer = Stemmer(None)

        with open(self.inputFile, "r") as file:
            for line in file:
                parser.line = line
                parser.parse()
                tokenizer.stringToTokenize = parser.text
                tokens = tokenizer.tokenize()
                self.buildDictionary(tokens, parser.docId)

                i += 1
                if i >= blocSize:
                    if self.stemmerOptions["stemming"] :
                        stemmer.tokenList = list(self.tempDict.keys())
                        tokensStemmed = stemmer.stem()
                        #We build a dict with the stemmed tokens in order to write the partial index
                        self.buildDictionaryAfterStemming(tokensStemmed)
                    self.writeTempDictInDisk(currentBloc)
                    self.tempDictAfterStemming = {}
                    self.tempDict = {}
                    i = 0
                    currentBloc += 1

        if self.tempDict:
            if self.stemmerOptions["stemming"] :
                stemmer.tokenList = list(self.tempDict.keys())
                tokensStemmed = stemmer.stem()
                #We build a dict with the stemmed tokens in order to write the partial index
                self.buildDictionaryAfterStemming(tokensStemmed)
            self.writeTempDictInDisk(currentBloc)
            self.tempDict = {}


    def buildDictionary(self, tokens, docId):

        i = 0
        for tok in tokens:
            if tok not in self.tempDict:
                self.tempDict[tok] = {docId: [i]}
            else:
                if docId not in self.tempDict[tok]:
                    self.tempDict[tok][docId] = [i]
                else:
                    self.tempDict[tok][docId].append(i)

            i += 1

    
    # "Duplicating" the tempDict only takes about 4 to 4.5 more seconds 
    # It's way faster (about 20 to 25 seconds of difference) to duplicate tempDict than using stemming before building tempDict
    def buildDictionaryAfterStemming(self, tokens):
        for originalToken, token in tokens:
            for docId in self.tempDict[originalToken] :
                if token not in self.tempDictAfterStemming:
                    self.tempDictAfterStemming[token] = {docId: self.tempDict[originalToken][docId]}
                else:
                    if docId in self.tempDictAfterStemming[token] :

                        #As we have a generator object, we have to iterate over it with next() 
                        #It is because we want to append the int inside the list, not the list itself
                        listToAppend = (i for i in self.tempDict[originalToken][docId])
                        #Boolean to stop the while loop
                        haveToAppend = True
                        while haveToAppend :
                            try :
                                toAppend = next(listToAppend)
                                self.tempDictAfterStemming[token][docId].append(toAppend)
                            except StopIteration :
                                haveToAppend=False
                    else :
                        self.tempDictAfterStemming[token][docId] = self.tempDict[originalToken][docId]
                #Clearing the copied list
                self.tempDict[originalToken][docId] = []

    def writeTempDictInDisk(self, currentBloc):
        if not os.path.exists(self.outputDirectory):
            os.mkdir(self.outputDirectory)
        if self.stemmerOptions["stemming"]:
            self.tempDictAfterStemming = dict(sorted(self.tempDictAfterStemming.items()))
            with open(f"{self.outputDirectory}/indexPart{currentBloc}.jsonl", "w") as file:
                for key, value in self.tempDictAfterStemming.items():
                    file.write(json.dumps({key: value}) + "\n")
        else:
            self.tempDict = dict(sorted(self.tempDict.items()))
            with open(f"{self.outputDirectory}/indexPart{currentBloc}.jsonl", "w") as file:
                for key, value in self.tempDict.items():
                    file.write(json.dumps({key: value}) + "\n")