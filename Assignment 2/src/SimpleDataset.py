import json
import random
import torch

class SimpleDataset(torch.utils.data.Dataset):
    def __init__(self, questionFile, questionsRankedFile, medlineFile, tokenizer):
        super().__init__()
        with open(questionFile, 'r') as f:
            self.questionLines = f.readlines()
        with open(questionsRankedFile, 'r') as f:
            self.questionsRankedLines = f.readlines()
        with open(medlineFile, 'r') as f:
            self.medlineLines = f.readlines()
        self.tokenizer = tokenizer
        # load your data here

    def __len__(self):
        return len(self.questionLines)

    def __getitem__(self, idx):
        question = self.questionLines[idx]
        question = json.loads(question)
        question_id = question["query_id"]
        question_text = question["question"]
        goldstandard_documents = question["goldstandard_documents"]

        # Get positives

        number_goldstandard_documents = len(goldstandard_documents)
        index = random.randint(0, number_goldstandard_documents - 1)
        positive_id = goldstandard_documents[index]
        for line in self.medlineLines:
            line = json.loads(line)
            if line["doc_id"] == positive_id:
                positive_text = line["text"]
                break

        # Get negatives
        
        number_documents = len(self.medlineLines)
        index = random.randint(0, number_documents - 1)
        negative_document = json.loads(self.medlineLines[index])
        negative_id = negative_document["doc_id"]
        negative_text = negative_document["text"]

        while negative_id in goldstandard_documents:
            index = random.randint(0, number_documents - 1)
            negative_document = json.loads(self.medlineLines[index])
            negative_id = negative_document["doc_id"]
            negative_text = negative_document["text"]        

        # Chose random 1/2

        if random.randint(0, 1) == 0:
            document_id = positive_id 
            document_text = positive_text
        else  :
            document_id = negative_id
            document_text = negative_text

        # Tokenize the texts
        print(document_text)
        question_token_ids = self.tokenizer(question_text)
        document_token_ids = self.tokenizer(document_text)

        # get the sample corresponding to index "idx"
        return {
            "question_id":question_id,
            "document_id":document_id,
            "question_token_ids": question_token_ids,
            "document_token_ids": document_token_ids,
        }