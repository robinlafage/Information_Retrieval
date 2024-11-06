import json
import math
import nltk.stem.porter as stemmerLibrary
from indexer.tokenizer import *

class Searcher:
    def __init__(self, indexDirectory, outputFile, searcherOptions):
        self.indexDirectory = indexDirectory
        self.outputFile = outputFile
        self.searcherOptions = searcherOptions
        self.scores = {}
        self.corpusInfos = {}

    def search(self):
        print("Searching...")
        
        with open("../indexes/documentsLength.json", 'r') as file:
            self.corpusInfos = json.load(file)

        N = self.corpusInfos["nbDocuments"]
        avdl = self.corpusInfos["avdl"]

        tokenizer = Tokenizer(None, self.corpusInfos["metadata"]["minimumTokenLength"], self.corpusInfos["metadata"]["normalizeToLower"], self.corpusInfos["metadata"]["allowedCharactersFile"], self.corpusInfos["metadata"]["stopwordsFile"])


        foundDocs = 0
        totalDocs = 0
        with open(self.searcherOptions["queryFile"], 'r') as file:
            for line in file:
                query = json.loads(line)
                print("Query: " + query["question"])
                self.searchQuery(query, N, avdl, tokenizer)
                self.scores = dict(sorted(self.scores.items(), key=lambda item: item[1], reverse=True))
                self.scores = {k: self.scores[k] for k in list(self.scores)[:100]}
                self.writeOutput(query)
                a, b = self.checkScores(query)
                foundDocs += a
                totalDocs += b
                self.scores = {}

        print(f"\033[31m Total: {foundDocs} / {totalDocs} \033[0m")

    #TODO: test with stemming
    def searchQuery(self, query, N, avdl, tokenizer):
        tokenizer.stringToTokenize = query["question"]
        terms = tokenizer.tokenize()

        for term in terms:
            if self.corpusInfos["metadata"]["stemming"]:
                term = stemmerLibrary.PorterStemmer().stem(term)

            try:
                if term[-1] == "?":
                    term = term[:-1]
                with open(self.indexDirectory + "/index_by_character_" + term[0] + ".jsonl", 'r') as file:
                    for line in file:
                        jsonLine = json.loads(line)
                        if list(jsonLine.keys())[0] == term:
                            print(f"term found: {term}")
                            self.calculateScore(jsonLine[term], N, avdl)

            except Exception as e:
                print(f"erreur : {e}")



    def calculateScore(self, line, N, avdl):
        k1 = self.searcherOptions["k1"]
        b = self.searcherOptions["b"]
        df = len(line)
        for doc in list(line.keys()):
            tf = len(line[doc])
            dl = self.corpusInfos["documentsLength"][doc]
            score = math.log(N / df) * (tf * (k1 + 1)) / (tf + k1 * ((1 - b) + b * (dl / avdl)))
            if doc in self.scores:
                self.scores[doc] += score
            else:
                self.scores[doc] = score


    def checkScores(self, query):
        foundDocs = 0
        for doc in query["goldstandard_documents"]:
            if doc in self.scores:
                foundDocs += 1
            
        print(f"\033[31m Found documents: {foundDocs} / {len(query['goldstandard_documents'])} \033[0m")

        return foundDocs, len(query["goldstandard_documents"])


    def writeOutput(self, query):
        outputJson = {}

        outputJson["id"] = query["query_id"]
        outputJson["question"] = query["question"]
        outputJson["retrieved_documents"] = list(self.scores.keys())

        outputJson = json.dumps(outputJson)
        with open(self.outputFile, 'a') as file:
            file.write(outputJson + "\n")


if __name__ == '__main__':
    searcher = Searcher("indexDirectory", "outputFile", {"queryFile": "queryFile", "k1": 1.2, "b": 0.75, "maximumDocuments": 100})
    # print(searcher.averageWordCount("../corpus/a.jsonl"))
    # print(searcher.wordCount("../corpus/MEDLINE_2024_Baseline.jsonl", "PMID:36839181"))