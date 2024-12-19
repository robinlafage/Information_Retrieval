from tokenizer import Tokenizer
from CNNInteractionBasedModel import CNNInteractionBasedModel
import torch
import json
import time
import gc
from ndcgMetric import NDCG

def reranker(modelFile, medline, inputFile, outputFile):

    device = torch.device('cpu')
    
    #Loading tokenizer data and embedding matrix
    tokenizer = Tokenizer()
    embedding_matrix = torch.load('../model_data/embedding_matrix.pth', weights_only=True)
    with open('../model_data/tokenizer.json', 'r') as f:
        tokenizer.token_to_id = json.load(f)
        tokenizer.vocab_size = len(tokenizer.token_to_id)
    with open('../model_data/padding_size.txt', 'r') as f:
        tokenizer.padding_size = int(f.read())

    # Initialisation du modèle
    model = CNNInteractionBasedModel(tokenizer.vocab_size, embedding_matrix)
    checkpoint = torch.load(modelFile, weights_only=True, map_location=torch.device('cpu'))

    model.load_state_dict(checkpoint, strict=True)
    model.eval()   
    model.to(device)

    maxNumberOfDocs = 4
    retrievedDocs = inputFile
    output = outputFile

    with open(retrievedDocs, 'r') as f:
        line1 = f.readline()
        line1 = json.loads(line1)
        if type(line1['retrieved_documents'][0]) == dict:
            changeInputFileFormat(retrievedDocs, "../inputFileReformatted.jsonl")
            retrievedDocs = "../inputFileReformatted.jsonl"
        f.seek(0)


    with open(retrievedDocs, 'r') as f:
        for line in f:
            line = json.loads(line)
            query = line['question']
            print(query)
            query_ids = tokenizer(query)
            if len(query_ids) < 6:
                query_ids = query_ids + [0] * (6 - len(query_ids))
            docsIds = line['retrieved_documents']

            docs = {}
            with open(medline, 'r') as medlineFile:
                for doc in medlineFile:
                    doc = json.loads(doc)
                    if doc['doc_id'] in docsIds:
                        docs[doc['doc_id']] = doc['text']
                        docsIds.remove(doc['doc_id'])
                    if len(docsIds) == 0:
                        break

            probs = {}
            if len(docs) == 1 :
                for doc in docs:
                    probs[doc] = 1

            else :
                for i in range(0, len(docs), maxNumberOfDocs):
                    currentDocs = list(docs.keys())[i:i+maxNumberOfDocs]

                    docsTokens = []
                    max_document_len = 0
                    
                    for doc in currentDocs:
                        doc_ids = tokenizer(docs[doc])
                        docsTokens.append(doc_ids)
                        if len(doc_ids) > max_document_len :
                            max_document_len = len(doc_ids)

                    docsTokens2 = []
                    for doc in docsTokens :
                        if len(doc) > max_document_len:
                            docsTokens2.append(doc[:max_document_len])
                        else:
                            docsTokens2.append(doc + [0] * (max_document_len - len(doc)))
                        

                    document_ids = torch.stack([torch.tensor(docTokens) for docTokens in docsTokens2])
                    query_ids = torch.tensor(query_ids)
                    a = model(query_ids, document_ids)

                    del docsTokens
                    del docsTokens2
                    del document_ids
                    gc.collect()

                    for j, doc in enumerate(currentDocs):
                        probs[doc] = a.tolist()[j] if type(a.tolist()) == list else a.tolist()
                        probs[doc] = [probs[doc]] if type(probs[doc]) != list else probs[doc]
                    
                    del currentDocs
                    del a
                    gc.collect()
                    

            probs = {k: v for k, v in sorted(probs.items(), key=lambda item: item[1], reverse=True)}
            with open(output, 'a') as output_file:
                output_file.write(json.dumps({"query_id": line['id'], "question": query, "retrieved_documents": list(probs.keys())}) + '\n')

            del probs
            del docs
            del docsIds
            del query_ids
            del query
            del line
            gc.collect()




def changeInputFileFormat(inputFile, outputFile):
    # Delete outputFile content
    with open(outputFile, "w") as f:
        pass

    with open(inputFile, "r") as f:
        output = {}
        for line in f:
            data = json.loads(line)
            query_id = data["query_id"]
            output["id"] = query_id
            with open("../questions.jsonl", "r") as q:
                for line in q:
                    question = json.loads(line)
                    if question["query_id"] == query_id:
                        output["question"] = question["question"]
                        break

            output["retrieved_documents"] = [doc["id"] for doc in data["retrieved_documents"]]

            with open(outputFile, "a") as out:
                out.write(json.dumps(output) + "\n")