import json
import math
import nltk.stem.porter as stemmerLibrary
from indexer.tokenizer import *
import time
from searcher.ndcgMetric import *
from itertools import islice

class Searcher:
    def __init__(self, indexDirectory, outputFile, searcherOptions):
        self.indexDirectory = indexDirectory
        self.outputFile = outputFile
        self.searcherOptions = searcherOptions
        self.scores = {}
        self.corpusInfos = {}
        self.totalNdcg = 0

    def search(self):
        """
        Search for the queries (from a file or from user input) in the index
        """
        
        with open(f"{self.indexDirectory}/documentsLength.json", 'r') as file:
            self.corpusInfos = json.load(file)

        N = self.corpusInfos["nbDocuments"]
        avdl = self.corpusInfos["avdl"]
        tokenizer = Tokenizer(None, self.corpusInfos["metadata"]["minimumTokenLength"], self.corpusInfos["metadata"]["normalizeToLower"], self.corpusInfos["metadata"]["allowedCharactersFile"], self.corpusInfos["metadata"]["stopwordsFile"])

        if self.searcherOptions["queryFile"]:
            self.searchAllQueries(N, avdl, tokenizer)
        else:
            self.interactiveSearch(N, avdl, tokenizer)
        

    def searchAllQueries(self, N, avdl, tokenizer):
        """
        Search for all the queries in the query file

        Args:
            N (int): Number of documents in the corpus
            avdl (float): Average document length
            tokenizer (Tokenizer): Tokenizer object
        """
        with open(self.searcherOptions["queryFile"], 'r') as file:
            for line in file:
                query = json.loads(line)
                print("Query: " + query["question"])
                self.searchQuery(query, N, avdl, tokenizer)
                self.scores = dict(sorted(self.scores.items(), key=lambda item: item[1], reverse=True))
                self.scores = {k: self.scores[k] for k in list(self.scores)[:self.searcherOptions["maximumDocuments"]]}
                self.writeOutput(query)
                self.scores = {}


    def interactiveSearch(self, N, avdl, tokenizer):
        """
        Search for queries interactively

        Args:
            N (int): Number of documents in the corpus
            avdl (float): Average document length
            tokenizer (Tokenizer): Tokenizer object
        """
        id = 0
        while True:
            query = input("Enter your query: (type 'exit' to leave)\n")
            if query == "exit":
                break

            query = {"question": query, "query_id": str(id)}
            self.searchQuery(query, N, avdl, tokenizer)
            self.scores = dict(sorted(self.scores.items(), key=lambda item: item[1], reverse=True))
            self.scores = {k: self.scores[k] for k in list(self.scores)[:100]}
            self.writeOutput(query)
            self.scores = {}
            id += 1

    def searchQuery(self, query, N, avdl, tokenizer):
        """
        Search for one query in the index

        Args:
            query (dict): Query to search
            N (int): Number of documents in the corpus
            avdl (float): Average document length
            tokenizer (Tokenizer): Tokenizer object
        """
        tokenizer.stringToTokenize = query["question"]
        terms = tokenizer.tokenize()
        stepSize = 1000
        indexSup = 0
        found = False

        for term in terms:
            if self.corpusInfos["metadata"]["stemming"]:
                term = stemmerLibrary.PorterStemmer().stem(term)

            try:
                with open(self.indexDirectory + "/index_by_character_" + term[0] + ".jsonl", 'r') as file:
                    slice = list(islice(file, 0, None, stepSize))
                    found=False
                    for index, line in enumerate(slice) :
                        jsonLine = json.loads(line)
                        indexSup = index
                        if list(jsonLine.keys())[0] == term :
                            found = True
                            self.calculateScore(jsonLine[term], N, avdl)
                            break
                        if list(jsonLine.keys())[0] > term :
                            break
                    else :
                        file.seek(0)
                        slice = list(islice(file, indexSup*stepSize, None, 1))
                        for line in slice :
                            jsonLine = json.loads(line)
                            if list(jsonLine.keys())[0] == term :
                                found=True
                                self.calculateScore(jsonLine[term], N, avdl)
                                break
                    if indexSup != 0 and not found :
                        file.seek(0)
                        slice = list(islice(file, (indexSup-1)*stepSize, indexSup*stepSize, 1))
                        for line in slice :
                            jsonLine = json.loads(line)
                            if list(jsonLine.keys())[0] == term :
                                found = True
                                self.calculateScore(jsonLine[term], N, avdl)
                                break

            except Exception as e:
                print(f"Error : {e}")



    def calculateScore(self, line, N, avdl):
        """
        Calculate the document score for a query term

        Args:
            line (dict): Line of the index
            N (int): Number of documents in the corpus
            avdl (float): Average document length
        """

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


    def writeOutput(self, query):
        """
        Write the query results in the output file

        Args:
            query (dict): Query treated
        """
        
        outputJson = {}

        outputJson["id"] = query["query_id"]
        outputJson["question"] = query["question"]
        outputJson["retrieved_documents"] = list(self.scores.keys())

        outputJson = json.dumps(outputJson)
        with open(self.outputFile, 'a') as file:
            file.write(outputJson + "\n")