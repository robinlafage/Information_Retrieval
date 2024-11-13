from indexer.parser import *
from indexer.tokenizer import *
from indexer.stemmer import *
from indexer.merger import *
import json

class Indexer:
    def __init__(self, inputFile, outputDirectory, tokenizerOptions, stemmerOptions):
        self.inputFile = inputFile
        self.outputDirectory = outputDirectory
        self.tokenizerOptions = tokenizerOptions
        self.stemmerOptions = stemmerOptions
        self.tempDict = {}
        self.tempDictAfterStemming = {}
        self.temporaryIndexesDirectory = "../tmpIndexes"

    def buildIndex(self):
        #Cleaning the temporaryIndexesDirectory before building the index
        filesInTemporaryDirectory = None 
        if os.path.exists(self.temporaryIndexesDirectory):
            filesInTemporaryDirectory = [f for f in os.listdir(self.temporaryIndexesDirectory) if os.path.isfile(os.path.join(self.temporaryIndexesDirectory, f))]
        if len(filesInTemporaryDirectory) > 0 :
            print('Suppressing all the files in the temporary directory')
            for file in filesInTemporaryDirectory :
                os.remove(f"{self.temporaryIndexesDirectory}/{file}")
            print('Finished suppressing all the files in the temporary directory')
        self.buildPartialsIndexes()
        merger = Merger(self.inputFile, self.outputDirectory, self.tokenizerOptions, self.stemmerOptions, self.temporaryIndexesDirectory)
        merger.merge()
        self.getDocumentsLength()


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
        if not os.path.exists(self.temporaryIndexesDirectory):
            os.mkdir(self.temporaryIndexesDirectory)
        if self.stemmerOptions["stemming"]:
            self.tempDictAfterStemming = dict(sorted(self.tempDictAfterStemming.items()))
            with open(f"{self.temporaryIndexesDirectory}/indexPart{currentBloc}.jsonl", "w") as file:
                for key, value in self.tempDictAfterStemming.items():
                    file.write(json.dumps({key: value}) + "\n")
        else:
            self.tempDict = dict(sorted(self.tempDict.items()))
            with open(f"{self.temporaryIndexesDirectory}/indexPart{currentBloc}.jsonl", "w") as file:
                for key, value in self.tempDict.items():
                    file.write(json.dumps({key: value}) + "\n")


    def getDocumentsLength(self):
        tokenizer = Tokenizer(None, 
                              1, #We always count every words
                              self.tokenizerOptions["normalizeToLower"], 
                              self.tokenizerOptions["allowedCharactersFile"], 
                              "") #We always count stopwords in the documents length

        totalWords = 0
        totalDocuments = 0
        outPutJson = {}

        documentsLength = {}
        with open(self.inputFile, "r") as file:
            for line in file:
                document = json.loads(line)
                documentContent = document["text"]
                tokenizer.stringToTokenize = documentContent
                tokens = tokenizer.tokenize()
                documentLen = len(tokens)
                documentsLength[document["doc_id"]] = documentLen

                totalWords += documentLen
                totalDocuments += 1

        avdl = totalWords / totalDocuments
        outPutJson["metadata"] = self.defineMetadata()
        outPutJson["nbDocuments"] = totalDocuments
        outPutJson["avdl"] = avdl
        outPutJson["documentsLength"] = documentsLength

        with open("../indexes/documentsLength.json", "w") as file:
            file.write(json.dumps(outPutJson))


    def defineMetadata(self):
        metadata = {}
        metadata["stemming"]=self.stemmerOptions["stemming"]
        metadata["minimumTokenLength"]=self.tokenizerOptions["minimumTokenLength"]
        metadata["normalizeToLower"]=self.tokenizerOptions["normalizeToLower"]
        metadata["allowedCharactersFile"]=self.tokenizerOptions["allowedCharactersFile"]
        metadata["stopwordsFile"]=self.tokenizerOptions["stopwordsFile"]
        return metadata