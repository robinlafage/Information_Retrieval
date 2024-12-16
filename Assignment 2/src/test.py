import json

with open("../documents/questions_bm25_ranked.jsonl", "r") as f:
    output = {}
    for line in f:
        data = json.loads(line)
        query_id = data["query_id"]
        output["id"] = query_id
        with open("../documents/questions.jsonl", "r") as q:
            for line in q:
                question = json.loads(line)
                if question["query_id"] == query_id:
                    output["question"] = question["question"]
                    break

        output["retrieved_documents"] = [doc["id"] for doc in data["retrieved_documents"]]

        with open("../documents/retrieved_docs_prof.jsonl", "a") as out:
            out.write(json.dumps(output) + "\n")