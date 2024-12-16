import json
import random
import torch

class SimpleDataset(torch.utils.data.Dataset):
    def __init__(self, questionFile, medlineFile, tokenizer):
        super().__init__()
        with open(questionFile, 'r') as f:
            self.questionLines = f.readlines()
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

        positive_text = None
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

        if random.randint(0, 1) == 0 :
            document_id = positive_id 
            document_text = positive_text
        else  :
            document_id = negative_id
            document_text = negative_text

        # Tokenize the texts
        # print(document_text)
        question_token_ids = self.tokenizer(question_text)
        document_token_ids = self.tokenizer(document_text)

        # get the sample corresponding to index "idx"
        return {
            "question_id":question_id,
            "document_id":document_id,
            "question_token_ids": question_token_ids,
            "document_token_ids": document_token_ids,
        }


def build_collate_fn(tokenizer, max_number_of_question_tokens, max_number_of_document_tokens, device):
  def collate_fn(batch):
    """
    batch : list of samples from the dataset

    The gold is to pad the question and the document to a uniform size "standard size"
    you can assume max_number_of_question_tokens and max_number_of_document_tokens as the
    maximum values allow within the batch or you can compute yourself a dynamic value based on
    the largest sample in the batch.

    The question_id and document_id can not be tensors since they are not feed to the model

    returns: tensor or a dictionary of tensors.
    """

    question_token_ids = []
    document_token_ids = []
    question_ids = []
    document_ids = []

    for sample in batch:
        question_ids.append(sample["question_id"])
        document_ids.append(sample["document_id"])

        question_tokens = sample["question_token_ids"]
        if len(question_tokens) > max_number_of_question_tokens:
            question_token_ids.append(question_tokens[:max_number_of_question_tokens])
        else:
            question_token_ids.append(question_tokens + [0] * (max_number_of_question_tokens - len(question_tokens)))

        document_tokens = sample["document_token_ids"]
        if len(document_tokens) > max_number_of_document_tokens:
            document_token_ids.append(document_tokens[:max_number_of_document_tokens])
        else:
            document_token_ids.append(document_tokens + [0] * (max_number_of_document_tokens - len(document_tokens)))

        
    # print(f"question_id : {question_ids}")
    # print(f"document_id : {document_ids}")
    # print(f"question_token_ids : {question_token_ids}")
    # print(f"document_token_ids : {document_token_ids}")



    return {
            "queries": torch.tensor(question_token_ids, dtype=torch.long, device=device),
            "documents": torch.tensor(document_token_ids, dtype=torch.long, device=device),
            "question_id": question_ids,
            "document_id": document_ids, 
        }
  return collate_fn

