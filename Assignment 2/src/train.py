from tokenizer import Tokenizer
from CNNInteractionBasedModel import CNNInteractionBasedModel
from LoadingPreTrainedEmbeddings import LoadingPreTrainedEmbeddings
import torch
from SimpleDataset import SimpleDataset, build_collate_fn
import json
import time

def train(medline, questions, gloveFile, outputFile):
    start = time.time()
    device = torch.device('cuda')
    print(f"Utilisation de l'appareil : {device}")
    
    tokenizer = Tokenizer()

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
    embeddings_index = loadingPreTrainedEmbeddings.load_glove_embeddings(gloveFile)

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
        medline,
        tokenizer
    )

    # Définition de la fonction de padding
    collate_fn_question_documents_padding = build_collate_fn(
        tokenizer, max_number_of_question_tokens=200, max_number_of_document_tokens=2000, device=device
    )

    # DataLoader
    train_loader = torch.utils.data.DataLoader(
        train_dataset,
        batch_size=16,
        shuffle=True,
        collate_fn=collate_fn_question_documents_padding
    )
    
    criterion = torch.nn.MarginRankingLoss(margin=1.0)  # Exemple pour classification
    optimizer = torch.optim.Adam(model.parameters(), lr=0.0001)

    print("Début de l'entraînement...")
    start_training = time.time()
    num_epochs = 10
    for epoch in range(num_epochs):
        model.train()
        running_loss = 0.0
        i=0
        start_epoch = time.time()
        for batch in train_loader:
            # Récupérer les données du batch
            queries = batch['queries']
            positive_documents = batch['positive_documents']
            negative_documents = batch['negative_documents']

            # Forward pass (prédiction des scores)
            output_pertinent = model(queries, positive_documents)  # Score pour le document pertinent
            output_not_pertinent = model(queries, negative_documents)  # Score pour le document non pertinent

            # Cible : 1 si le document pertinent est supérieur au non pertinent
            targets = torch.ones_like(output_pertinent)  # 1 pour les paires pertinentes

            # Calcul de la perte
            loss = criterion(output_pertinent, output_not_pertinent, targets)

            # Backpropagation et mise à jour des poids
            optimizer.zero_grad()  # Réinitialiser les gradients
            loss.backward()  # Calcul des gradients
            optimizer.step()  # Mise à jour des paramètres du modèle

            running_loss += loss.item()
            i+=1
            print(f'Part {((i-1)*16)} to {(i*16)-1} of the batch')
        end_epoch = time.time()
        torch.save(model.state_dict(), f'../model_data2/model_temp{epoch+1}.pth')
        
        print(f'Durée de l\'époque : {(end_epoch-start_epoch)/60} minutes')
        print(f"Époque {epoch + 1}/{num_epochs}, Perte moyenne : {running_loss / len(train_loader):.4f}")

    torch.save(model.state_dict(), outputFile)
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

