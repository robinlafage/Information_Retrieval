from parser import *
from tokenizer import *
from stemmer import *
import json
import ijson

#BUG : If the destination directory doesn't already exist, we crash 

class Indexer:
    def __init__(self, inputFile, outputFile, tokenizerOptions, stemmerOptions):
        self.inputFile = inputFile
        self.outputFile = outputFile
        self.tokenizerOptions = tokenizerOptions
        self.stemmerOptions = stemmerOptions
        self.tempDict = {}
        self.tempDictAfterStemming = {}

    def buildIndex(self):
        blocSize = 1000
        i = 0
        currentBloc = 0

        parser = Parser(None)
        tokenizer = Tokenizer(None, 
                              self.tokenizerOptions["minimumTokenLength"], 
                              self.tokenizerOptions["normalizeToLower"], 
                              self.tokenizerOptions["cuttingCharactersFile"], 
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
        if self.stemmerOptions["stemming"] :
            self.tempDictAfterStemming = dict(sorted(self.tempDictAfterStemming.items()))
            with open(f"../tmpIndexesStemmer/indexPart{currentBloc}.json", "w") as file:
                file.write(json.dumps(self.tempDictAfterStemming))
        else :
            self.tempDict = dict(sorted(self.tempDict.items()))
            with open(f"../tmpIndexesNoStemmer/indexPart{currentBloc}.json", "w") as file:
                file.write(json.dumps(self.tempDict))


    # def writeTempDictInDisk(self, currentBloc):
    #     self.tempDict = dict(sorted(self.tempDict.items()))
    #     with open(f"../tmpIndexes/indexPart{currentBloc}.json", "w") as file:
    #         file.write(json.dumps(self.tempDict))


    def merge2Indexes(self, a, b):
        nbLines = 100
        maxTerms = 1000

        with open(f"../tmpIndexes/indexPart{a}.jsonl", "r") as index1, open(f"../tmpIndexes/indexPart{b}.jsonl", "r") as index2:
            while True:
                index1Lines = [json.loads(line) for line in [index1.readline() for _ in range(nbLines)] if line]
                index2Lines = [json.loads(line2) for line2 in [index2.readline() for _ in range(nbLines)] if line2]

                if not index1Lines and not index2Lines:
                    break

                i1 = 0
                i2 = 0
                term1 = None
                term2 = None
                
                while i1 < len(index1Lines) or i2 < len(index2Lines):
                    if i1 == len(index1Lines):
                        term1 = None
                    else:
                        term1 = list(index1Lines[i1].keys())[0]

                    if i2 == len(index2Lines):
                        term2 = None
                    else:
                        term2 = list(index2Lines[i2].keys())[0]

                    termToTreat = 0
                    if term1 is not None and term2 is not None:
                        if term1 < term2:
                            termToTreat = 1
                        elif term1 > term2:
                            termToTreat = 2
                        else:
                            termToTreat = 3
                    elif term1 is not None:
                        termToTreat = 1
                    elif term2 is not None:
                        termToTreat = 2

                    if termToTreat == 1:
                        self.tempDict.update(index1Lines[i1])
                        i1 += 1
                    elif termToTreat == 2:
                        self.tempDict.update(index2Lines[i2])
                        i2 += 1
                    elif termToTreat == 3:
                        d = self.merge2Dicts(index1Lines[i1], index2Lines[i2], term1)
                        self.tempDict.update(d)
                        d.clear()
                        i1 += 1
                        i2 += 1

                    if len(self.tempDict) >= maxTerms:
                        self.appendToIndex(self.tempDict)
                        self.tempDict = {}

        if self.tempDict:
            self.appendToIndex(self.tempDict)
            self.tempDict = {}


        with open(self.outputFile, "a+") as file:
            file.write("}")
                
    
    
    def appendToIndex(self, tmpDict):
        with open(self.outputFile, "a+") as file:
            if file.tell() == 0:
                file.write("{")
            else:
                file.seek(file.tell() - 1)
                file.write(", ")

            for key, dict2 in tmpDict.items():
                file.write(f"\"{key}\": {{")
                for i, (key2, value) in enumerate(dict2.items()):
                    file.write(f"\"{key2}\": {value}")
                    if i < len(dict2) - 1:
                        file.write(", ")
                file.write("}")
                if list(tmpDict.keys())[-1] != key:
                    file.write(", ")
    


    def merge2Dicts(self, d1, d2, term):
        res = d1.copy()
        res[term].update(d2[term])
        return res