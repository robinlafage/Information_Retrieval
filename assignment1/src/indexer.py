from parser import *
from tokenizer import *
import json

class Indexer:
    def __init__(self, inputFile, outputFile, tokenizerOptions):
        self.inputFile = inputFile
        self.outputFile = outputFile
        self.tokenizerOptions = tokenizerOptions
        self.tempDict = {}

    def buildIndex(self):
        blocSize = 10000
        i = 0
        currentBloc = 0

        parser = Parser(None)
        tokenizer = Tokenizer(None, self.tokenizerOptions["minimumTokenLength"], " .,;\'\"-_`@~\\/?!()[]\{\}", [])

        with open(self.inputFile, "r") as file:
            for line in file:

                parser.line = line
                parser.parse()
                tokenizer.string = parser.text
                tokens = tokenizer.tokenize()
                self.buildDictionary(tokens, parser.docId)

                i += 1
                if i >= blocSize:
                    self.writeTempDictInDisk(currentBloc)
                    self.tempDict = {}
                    i = 0
                    currentBloc += 1

        if self.tempDict:
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
                


    def writeTempDictInDisk(self, currentBloc):
        self.tempDict = dict(sorted(self.tempDict.items()))
        with open(f"../index/indexPart{currentBloc}.json", "w") as file:
            file.write(json.dumps(self.tempDict))