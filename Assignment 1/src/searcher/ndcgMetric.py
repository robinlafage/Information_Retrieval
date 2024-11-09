import json
import math
import numpy as np
from sklearn.metrics import ndcg_score

class NDCG:
    def __init__(self, queries, scores):
        self.queries = queries
        self.scores = scores
        self.metric = 0


    def computeMetric(self):
        k = 10
        totalNdcg = 0

        with open(self.queries, 'r') as queriesFile, open(self.scores, 'r') as scoresFile:
            i = 0
            for query_line, response_line in zip(queriesFile, scoresFile):
                query = json.loads(query_line)
                response = json.loads(response_line)

                results = response["retrieved_documents"]
                relevant_set = set(query["goldstandard_documents"])

                ndcg = self.calculateNdcg(results, relevant_set, k)
                print(f"nDCG@{k}: {ndcg}")
                totalNdcg += ndcg
                i += 1

        self.metric = totalNdcg / i
        print(f"Average nDCG@{k}: {self.metric}")


    def calculateNdcg(self, results, relevant_set, k):
        y_true = [1 if doc in relevant_set else 0 for doc in results[:k]]
        y_score = [1 / (i + 1) for i in range(len(results[:k]))] 

        y_true = np.array([y_true])
        y_score = np.array([y_score])

        ndcg = ndcg_score(y_true, y_score, k=k)
        
        return ndcg