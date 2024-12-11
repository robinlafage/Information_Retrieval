from tokenizer import Tokenizer
from CNNInteractionBasedModel import CNNInteractionBasedModel
from LoadingPreTrainedEmbeddings import LoadingPreTrainedEmbeddings
import torch
from SimpleDataset import SimpleDataset, build_collate_fn
import json
import time

def main():
    start = time.time()
    device = torch.device('cpu')
    print(f"Utilisation de l'appareil : {device}")
    
    tokenizer = Tokenizer()

    # Préparation des données
    medline = '../documents/MEDLINE_2024_Baseline.jsonl'
    with open(medline, 'r') as f:
        for doc in f:
            text = json.loads(doc)['text']
            tokenizer.fit(text)

    end = time.time()
    print(f'Tokenizing the medline : {end-start}sec')
    
    questions = '../documents/questions.jsonl'
    with open(questions, 'r') as f:
        for doc in f:
            text = json.loads(doc)['question']
            tokenizer.fit(text)

    
    end = time.time()
    print(f'Tokenizing all the files : {end-start}sec')

    # Chargement des embeddings GloVe
    loadingPreTrainedEmbeddings = LoadingPreTrainedEmbeddings()
    glove_file = "../glove/glove.6B.50d.txt"  # Chemin vers votre fichier .txt
    embeddings_index = loadingPreTrainedEmbeddings.load_glove_embeddings(glove_file)

    embedding_dim = 50  # Dimension choisie pour les embeddings
    vocab, embedding_matrix = loadingPreTrainedEmbeddings.create_glove_matrix(
        list(tokenizer.token_to_id.keys()), embeddings_index, embedding_dim
    )
    tokenizer.token_to_id = vocab

    # Initialisation du modèle
    model = CNNInteractionBasedModel(tokenizer.vocab_size, embedding_matrix)
    model.load_state_dict(torch.load('../model.pth'))
    model.eval()  # Mettre en mode évaluation   
    # model.to(device)  # Déplacement du modèle sur GPU/CPU

    question = "Which name is also used to describe the Amazon rainforest in English?"
    document = "The Amazon rainforest, also known in English as Amazonia or the Amazon Jungle"
    # question2 = "Which name is also used to describe the Amazon rainforest in English?"
    # document2 = "The Amazon rainforest, also known in English as Amazonia or the Amazon Jungle forever and ever and ever"
    query_ids = tokenizer(question)
    document_ids = tokenizer(document)

    if max(query_ids + document_ids) >= embedding_matrix.shape[0]:
        raise ValueError(f"Indice hors limite détecté. Max index : {max(query_ids + document_ids)}, Taille de la matrice d'embedding : {embedding_matrix.shape[0]}")

    print(query_ids)
    print(document_ids)
    print(len(query_ids))
    a = model(query_ids, document_ids)
    print(a)
    # # Chargement des données
    # ds = SimpleDataset(
    #     "../documents/questions.jsonl",
    #     "../documents/questions_bm25_ranked.jsonl",
    #     "../documents/MEDLINE_2024_Baseline.jsonl",
    #     tokenizer
    # )

    # # Définition de la fonction de padding
    # collate_fn_question_documents_padding = build_collate_fn(
    #     tokenizer, max_number_of_question_tokens=20, max_number_of_document_tokens=300, device=device
    # )

    # # DataLoader
    # dl = torch.utils.data.DataLoader(
    #     ds,
    #     batch_size=64,
    #     shuffle=False,
    #     collate_fn=collate_fn_question_documents_padding
    # )

    

    # # Initialisation des résultats
    # ranked_documents = {}

    # # Traitement par lots
    # with torch.no_grad():  # Désactivation de la grad pour l'inférence
    #     ranked_documents = {}
    #     for batch_samples in dl:
    #         # retuns a vector of probabilities for each sample in the batch
    #         # print(batch_samples)
    #         query_ids = batch_samples.pop("question_id")
    #         document_id = batch_samples.pop("document_id")
    #         probs = model(**batch_samples)

    #         for prob, query_id, document_id in zip(probs, query_ids, document_id):
    #             ranked_documents[query_id] = (document_id, prob.item())

    #     ranked_documents = dict(sorted(ranked_documents.items(), key=lambda x: x[1][1], reverse=True))
    #     print(ranked_documents)

    # # Tri des documents par probabilité décroissante
    # ranked_documents = dict(sorted(ranked_documents.items(), key=lambda x: x[1][1], reverse=True))
    # print(ranked_documents)
    # end = time.time()
    # print(f'Total execution time : {end-start}sec')

if __name__ == "__main__":
    main()
