from ndcgMetric import NDCG
ndcg = NDCG("../documents/questions.jsonl", "../output1.jsonl")
print(ndcg.computeMetric())