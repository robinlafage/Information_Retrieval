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
    # questions = '../documents/questions.jsonl'
    # medline = '../documents/MEDLINE_2024_Baseline.jsonl'
    results = "../documents/training_data_bm25_ranked.jsonl"
    medline = '../documents/MEDLINE_2024_Baseline.jsonl'
    questions = '../documents/training_data.jsonl'
    # Préparation des données
    with open(medline, 'r') as f:
        for doc in f:
            text = json.loads(doc)['text']
            tokenizer.fit(text)

    end = time.time()
    print(f'Tokenizing the medline : {end-start}sec')
    
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
    print(embedding_matrix.shape)

    # Initialisation du modèle
    print('creating model')
    model = CNNInteractionBasedModel(tokenizer.vocab_size, embedding_matrix)
    print('model created')
    checkpoint = torch.load('../model.pth')

    # Charger les poids sauvegardés pour la couche d'embedding
    # pretrained_weights = checkpoint['embedding_layer.weight']

    # # Dimensions attendues
    # current_vocab_size, embedding_dim = model.embedding_layer.weight.size()

    # # Ajuster les dimensions
    # if pretrained_weights.size(0) > current_vocab_size:
    #     # Tronquer les poids si le vocabulaire du checkpoint est plus grand
    #     pretrained_weights = pretrained_weights[:current_vocab_size, :]
    # elif pretrained_weights.size(0) < current_vocab_size:
    #     # Compléter avec des zéros si le vocabulaire du modèle est plus grand
    #     padding = torch.zeros((current_vocab_size - pretrained_weights.size(0), embedding_dim))
    #     pretrained_weights = torch.cat([pretrained_weights, padding], dim=0)

    # # Mettre à jour les poids dans le checkpoint
    # checkpoint['embedding_layer.weight'] = pretrained_weights

    # torch.save(checkpoint, '../adjusted_model.pth')



    model.load_state_dict(checkpoint, strict=False)
    print('model loaded')
    model.eval()  # Mettre en mode évaluation   
    print('Eval here')
    model.to(device)  # Déplacement du modèle sur GPU/CPU

    question = "What is the first indication for lurasidone?"
    document = "The development of lurasidone for bipolar depression.\n\nBipolar disorder is a chronic, recurrent illness that ranks among the top 10 causes of disability in the developed world. As the illness progresses, major depressive episodes increasingly predominate. However, few treatment options are available that have demonstrated efficacy in the treatment of bipolar depression, either as monotherapy or adjunctive therapy in combination with mood stabilizers. Lurasidone is an atypical antipsychotic drug that was initially developed for the treatment of schizophrenia. Since no previous atypical antipsychotic development program had proceeded directly from work on schizophrenia to bipolar depression, the decision to focus on this indication represented an innovation in central nervous system drug development and was designed to address a clinically significant unmet need. The current review summarizes key results of a clinical development program undertaken to characterize the efficacy and safety of lurasidone in patients diagnosed with bipolar depression. Lurasidone is currently the only treatment for bipolar depression approved in the United States as both a monotherapy and an adjunctive therapy with lithium or valproate. The approval of lurasidone expands available treatment options for patients with bipolar depression and provides a therapy with an overall favorable risk-benefit profile."
    document2 = "Interaction of Cep135 with a p50 dynactin subunit in mammalian centrosomes.\n\nCep135 is a 135-kDa, coiled-coil centrosome protein important for microtubule organization in mammalian cells [Ohta et al., 2002: J. Cell Biol. 156:87-99]. To identify Cep135-interacting molecules, we screened yeast two-hybrid libraries. One clone encoded dynamitin, a p50 dynactin subunit, which localized at the centrosome and has been shown to be involved in anchoring microtubules to centrosomes. The central domain of p50 binds to the C-terminal sequence of Cep135; this was further confirmed by immunoprecipitation and immunostaining of CHO cells co-expressing the binding domains for Cep135 and p50. Exogenous p50 lacking the Cep 135-binding domain failed to locate at the centrosome, suggesting that Cep135 is required for initial targeting of the centrosome. Altered levels of Cep135 and p50 by RNAi and protein overexpression caused the release of endogenous partner molecules from centrosomes. This also resulted in dislocation of other centrosomal molecules, such as gamma-tubulin and pericentrin, ultimately leading to disorganization of microtubule patterns. These results suggest that Cep135 and p50 play an important role in assembly and maintenance of functional microtubule-organizing centers."
    document3 = "Lurasidone: a new treatment option for bipolar depression-a review.\n\nDepressive episodes in bipolar disorder contribute to significant morbidity and mortality. Until recently, only quetiapine and an olanzapine-fluoxetine combination were approved to treat bipolar depression. Recently, lurasidone was approved to treat bipolar depression either as monotherapy or adjunctively with lithium or valproate. Lurasidone was well- tolerated, and commonly observed adverse reactions (incidence \u22655% and at least twice the rate for placebo) were akathisia, extrapyramidal symptoms, and somnolence. There were no significant metabolic or electrocardiogram abnormalities. It is taken with food to ensure maximal absorption, and dose should be adjusted in patients who receive moderate CYP450 inhibitors or inducers and in patients with renal disease."
    document4 = "Lurasidone: a novel antipsychotic agent for the treatment of schizophrenia and bipolar depression.\n\nLurasidone is a novel antipsychotic agent approved for the treatment of schizophrenia in a number of countries including the UK, and is also approved in the USA and Canada for the treatment of major depressive episodes associated with bipolar I disorder as either a monotherapy or adjunctive therapy with lithium or valproate. In addition to full antagonist activity at dopamine D2 (K i(D2) = 1 nM) and serotonin 5-HT2A (K i(5-HT2A) = 0.5 nM) receptors, the pharmacodynamic profile of lurasidone is notable for its high affinity for serotonin 5-HT7 receptors (K i(5-HT7) = 0.5 nM) and its partial agonist activity at 5-HT1A receptors (K i(5-HT1A) = 6.4 nM). Long-term treatment of schizophrenia with lurasidone has been shown to reduce the risk of relapse. Lurasidone appears associated with minimal effects on body weight and low risk for clinically meaningful alterations in glucose, lipids or electrocardiogram parameters."
    query_ids = tokenizer(question)
    document_ids = tokenizer(document)
    document_ids2 = tokenizer(document2)
    document_ids3 = tokenizer(document3)
    document_ids4 = tokenizer(document4)

    if max(query_ids + document_ids) >= embedding_matrix.shape[0]:
        raise ValueError(f"Indice hors limite détecté. Max index : {max(query_ids + document_ids)}, Taille de la matrice d'embedding : {embedding_matrix.shape[0]}")

    document_ids = torch.stack([torch.tensor(document_ids), torch.tensor(document_ids2), torch.tensor(document_ids3), torch.tensor(document_ids4)])
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
    #     tokenizer, max_number_of_question_tokens=200, max_number_of_document_tokens=3000, device=device
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
