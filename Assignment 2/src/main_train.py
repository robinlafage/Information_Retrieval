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
    results = "../documents/training_data_bm25_ranked.jsonl"
    medline = '../documents/MEDLINE_2024_Baseline.jsonl'
    questions = '../documents/training_data.jsonl'

    with open(medline, 'r') as f:
        for doc in f:
            text = json.loads(doc)['text']
            tokenizer.fit(text)
    
    with open(questions, 'r') as f:
        for doc in f:
            text = json.loads(doc)['question']
            tokenizer.fit(text)


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
    model.to(device)  # Déplacement du modèle sur GPU/CPU

    # Chargement des données
    train_dataset = SimpleDataset(
        questions,
        results,
        medline,
        tokenizer
    )

    # Définition de la fonction de padding
    collate_fn_question_documents_padding = build_collate_fn(
        tokenizer, max_number_of_question_tokens=200, max_number_of_document_tokens=3000, device=device
    )

    # DataLoader
    train_loader = torch.utils.data.DataLoader(
        train_dataset,
        batch_size=16,
        shuffle=True,
        collate_fn=collate_fn_question_documents_padding,
        num_workers=2
    )
    
    criterion = torch.nn.BCELoss()  # Exemple pour classification
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    num_epochs = 10
    print("Début de l'entraînement...")
    start_training = time.time()
    for epoch in range(num_epochs):
        start_epoch = time.time()
        model.train()
        running_loss = 0.0
        i=0
        for batch in train_loader:
            i+=1
            queries = batch['queries']
            documents = batch['documents']

            # Forward pass
            outputs = model(queries, documents)
            targets = torch.tensor([1.0 if qid == did else 0.0 for qid, did in zip(batch['question_id'], batch['document_id'])], device=device)

            loss = criterion(outputs, targets)

            # Backpropagation et mise à jour des poids
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            print(f'Part {((i-1)*16)} to {(i*16)-1} of the batch')
        end_epoch = time.time()
        torch.save(model.state_dict(), f'../model_temp{epoch+1}.pth')
        
        print(f'Durée de l\'époque : {(end_epoch-start_epoch)/60} minutes')
        print(f"Époque {epoch + 1}/{num_epochs}, Perte moyenne : {running_loss / len(train_loader):.4f}")

    torch.save(model.state_dict(), '../model.pth')
    end_training = time.time()
    print("Entraînement terminé.")
    print(f'Durée de l\'entrainement : {(end_training-start_training)/60} minutes')
    # # Initialisation des résultats
    # ranked_documents = {}

    # # Traitement par lots
    # with torch.no_grad():  # Désactivation de la grad pour l'inférence
    #     for batch_samples in dl:
    #         query_ids = batch_samples.pop("question_id")
    #         document_ids = batch_samples.pop("document_id")
            
    #         # Assurez-vous que les tenseurs sont sur le bon appareil
    #         for key in batch_samples.keys():
    #             batch_samples[key] = batch_samples[key].to(device)

    #         # Calcul des probabilités
    #         probs = model(**batch_samples)

    #         # Association des résultats
    #         for prob, query_id, document_id in zip(probs, query_ids, document_ids):
    #             ranked_documents[query_id] = (document_id, prob.item())

    # # Tri des documents par probabilité décroissante
    # ranked_documents = dict(sorted(ranked_documents.items(), key=lambda x: x[1][1], reverse=True))
    # print(ranked_documents)
    end = time.time()
    print(f'Total execution time : {end-start}sec')

if __name__ == "__main__":
    main()
