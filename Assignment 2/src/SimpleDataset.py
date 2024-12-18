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



        # Tokenize the texts
        # print(document_text)
        question_token_ids = self.tokenizer(question_text)
        negative_token_ids = self.tokenizer(negative_text)
        positive_token_ids = self.tokenizer(positive_text)

        # get the sample corresponding to index "idx"
        return {
            "question_id":question_id,
            "positive_id":positive_id,
            "negative_id":negative_id,
            "question_token_ids": question_token_ids,
            "positive_token_ids": positive_token_ids,
            "negative_token_ids": negative_token_ids,
        }

def remove_padding(sequence):
    """
    Supprime les 0 à la fin d'une séquence.
    
    Args:
        sequence (list[int]): Une liste de tokens potentiellement paddée avec des 0.
        
    Returns:
        list[int]: La séquence sans le padding (les 0 en fin).
    """
    while sequence and sequence[-1] == 0:  # Supprime les 0 à la fin
        sequence.pop()
    return sequence

def build_collate_fn(tokenizer, max_number_of_question_tokens, max_number_of_document_tokens, device):
    def collate_fn(batch):
        """
        batch : list of samples from the dataset
        Le but est de faire du padding pour la question et les documents à une taille uniforme.
        On peut utiliser max_number_of_question_tokens et max_number_of_document_tokens comme valeurs maximales
        ou calculer dynamiquement la taille la plus grande dans le batch.
        
        Renvoie : un dictionnaire de tensors.
        """
        
        # Listes pour collecter les tokens
        question_token_ids = []
        positive_document_token_ids = []
        negative_document_token_ids = []
        question_ids = []
        positive_document_ids = []
        negative_document_ids = []
        for sample in batch:
            sample["question_token_ids"] = remove_padding(sample["question_token_ids"])
            sample["positive_token_ids"] = remove_padding(sample["positive_token_ids"])
            sample["negative_token_ids"] = remove_padding(sample["negative_token_ids"])

        max_question_len = max(len(sample['question_token_ids']) for sample in batch)
        max_positive_document_len = max(len(sample['positive_token_ids']) for sample in batch)
        max_negative_document_len = max(len(sample['negative_token_ids']) for sample in batch)
        

        adaptative_max_number_of_question_tokens = min(max_number_of_question_tokens, max_question_len)
        max_temp = max(max_positive_document_len, max_negative_document_len)
        adaptative_max_number_of_document_tokens = min(max_number_of_document_tokens, max_temp)

        print(adaptative_max_number_of_question_tokens)
        print(adaptative_max_number_of_document_tokens)
        # Traitement de chaque échantillon du batch
        for sample in batch:
            question_ids.append(sample["question_id"])
            positive_document_ids.append(sample["positive_id"])
            negative_document_ids.append(sample["negative_id"])

            # Récupérer les tokens de la question et des documents
            question_tokens = sample["question_token_ids"]
            positive_document_tokens = sample["positive_token_ids"]
            negative_document_tokens = sample["negative_token_ids"]

            # Padding des tokens de la question
            if len(question_tokens) > adaptative_max_number_of_question_tokens:
                question_token_ids.append(question_tokens[:adaptative_max_number_of_question_tokens])
            else:
                question_token_ids.append(question_tokens + [0] * (adaptative_max_number_of_question_tokens - len(question_tokens)))

            # Padding des tokens du document pertinent
            if len(positive_document_tokens) > adaptative_max_number_of_document_tokens:
                positive_document_token_ids.append(positive_document_tokens[:adaptative_max_number_of_document_tokens])
            else:
                positive_document_token_ids.append(positive_document_tokens + [0] * (adaptative_max_number_of_document_tokens - len(positive_document_tokens)))

            # Padding des tokens du document non pertinent
            if len(negative_document_tokens) > adaptative_max_number_of_document_tokens:
                negative_document_token_ids.append(negative_document_tokens[:adaptative_max_number_of_document_tokens])
            else:
                negative_document_token_ids.append(negative_document_tokens + [0] * (adaptative_max_number_of_document_tokens - len(negative_document_tokens)))
        
        # Retourner un dictionnaire avec les tensors
        return {
            "queries": torch.tensor(question_token_ids, dtype=torch.long, device=device),
            "positive_documents": torch.tensor(positive_document_token_ids, dtype=torch.long, device=device),
            "negative_documents": torch.tensor(negative_document_token_ids, dtype=torch.long, device=device),
            "question_id": question_ids,
            "positive_document_id": positive_document_ids,
            "negative_document_id": negative_document_ids,
        }
    
    return collate_fn
