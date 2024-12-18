from tokenizer import Tokenizer
from CNNInteractionBasedModel import CNNInteractionBasedModel
import torch
import json
import time
import gc
from ndcgMetric import NDCG

def reranker(modelFile, medline, inputFile, outputFile):
    # questions = '../documents/questions.jsonl'
    # results = "../documents/training_data_bm25_ranked.jsonl"
    # medline = '../documents/MEDLINE_2024_Baseline.jsonl'
    # questions = '../documents/training_data.jsonl'
    # Préparation des données
    # with open(medline, 'r') as f:
    #     for doc in f:
    #         text = json.loads(doc)['text']
    #         tokenizer.fit(text)

    # end = time.time()
    # print(f'Tokenizing the medline : {end-start}sec')
    
    # with open(questions, 'r') as f:
    #     for doc in f:
    #         text = json.loads(doc)['question']
    #         tokenizer.fit(text)

    
    # end = time.time()
    # print(f'Tokenizing all the files : {end-start}sec')

    # # Chargement des embeddings GloVe
    # loadingPreTrainedEmbeddings = LoadingPreTrainedEmbeddings()
    # glove_file = "../glove/glove.6B.50d.txt"  # Chemin vers votre fichier .txt
    # embeddings_index = loadingPreTrainedEmbeddings.load_glove_embeddings(glove_file)

    # embedding_dim = 50  # Dimension choisie pour les embeddings
    # vocab, embedding_matrix = loadingPreTrainedEmbeddings.create_glove_matrix(
    #     list(tokenizer.token_to_id.keys()), embeddings_index, embedding_dim
    # )
    # tokenizer.token_to_id = vocab
    # print(embedding_matrix.shape)

    start = time.time()
    device = torch.device('cpu')
    print(f"Using the device : {device}")
    
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
            changeInputFileFormat(retrievedDocs, "../documents/inputFileReformatted.jsonl")
            retrievedDocs = "../documents/inputFileReformatted.jsonl"
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
                    

            # print(probs)
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


    ndcg = NDCG("../documents/questions.jsonl", output)
    print(ndcg.computeMetric())
            

    # question = "What is the first indication for lurasidone?"
    # document = "The development of lurasidone for bipolar depression.\n\nBipolar disorder is a chronic, recurrent illness that ranks among the top 10 causes of disability in the developed world. As the illness progresses, major depressive episodes increasingly predominate. However, few treatment options are available that have demonstrated efficacy in the treatment of bipolar depression, either as monotherapy or adjunctive therapy in combination with mood stabilizers. Lurasidone is an atypical antipsychotic drug that was initially developed for the treatment of schizophrenia. Since no previous atypical antipsychotic development program had proceeded directly from work on schizophrenia to bipolar depression, the decision to focus on this indication represented an innovation in central nervous system drug development and was designed to address a clinically significant unmet need. The current review summarizes key results of a clinical development program undertaken to characterize the efficacy and safety of lurasidone in patients diagnosed with bipolar depression. Lurasidone is currently the only treatment for bipolar depression approved in the United States as both a monotherapy and an adjunctive therapy with lithium or valproate. The approval of lurasidone expands available treatment options for patients with bipolar depression and provides a therapy with an overall favorable risk-benefit profile."
    # document2 = "Interaction of Cep135 with a p50 dynactin subunit in mammalian centrosomes.\n\nCep135 is a 135-kDa, coiled-coil centrosome protein important for microtubule organization in mammalian cells [Ohta et al., 2002: J. Cell Biol. 156:87-99]. To identify Cep135-interacting molecules, we screened yeast two-hybrid libraries. One clone encoded dynamitin, a p50 dynactin subunit, which localized at the centrosome and has been shown to be involved in anchoring microtubules to centrosomes. The central domain of p50 binds to the C-terminal sequence of Cep135; this was further confirmed by immunoprecipitation and immunostaining of CHO cells co-expressing the binding domains for Cep135 and p50. Exogenous p50 lacking the Cep 135-binding domain failed to locate at the centrosome, suggesting that Cep135 is required for initial targeting of the centrosome. Altered levels of Cep135 and p50 by RNAi and protein overexpression caused the release of endogenous partner molecules from centrosomes. This also resulted in dislocation of other centrosomal molecules, such as gamma-tubulin and pericentrin, ultimately leading to disorganization of microtubule patterns. These results suggest that Cep135 and p50 play an important role in assembly and maintenance of functional microtubule-organizing centers."
    # document3 = "Lurasidone: a new treatment option for bipolar depression-a review.\n\nDepressive episodes in bipolar disorder contribute to significant morbidity and mortality. Until recently, only quetiapine and an olanzapine-fluoxetine combination were approved to treat bipolar depression. Recently, lurasidone was approved to treat bipolar depression either as monotherapy or adjunctively with lithium or valproate. Lurasidone was well- tolerated, and commonly observed adverse reactions (incidence \u22655% and at least twice the rate for placebo) were akathisia, extrapyramidal symptoms, and somnolence. There were no significant metabolic or electrocardiogram abnormalities. It is taken with food to ensure maximal absorption, and dose should be adjusted in patients who receive moderate CYP450 inhibitors or inducers and in patients with renal disease."
    # document4 = "Lurasidone: a novel antipsychotic agent for the treatment of schizophrenia and bipolar depression.\n\nLurasidone is a novel antipsychotic agent approved for the treatment of schizophrenia in a number of countries including the UK, and is also approved in the USA and Canada for the treatment of major depressive episodes associated with bipolar I disorder as either a monotherapy or adjunctive therapy with lithium or valproate. In addition to full antagonist activity at dopamine D2 (K i(D2) = 1 nM) and serotonin 5-HT2A (K i(5-HT2A) = 0.5 nM) receptors, the pharmacodynamic profile of lurasidone is notable for its high affinity for serotonin 5-HT7 receptors (K i(5-HT7) = 0.5 nM) and its partial agonist activity at 5-HT1A receptors (K i(5-HT1A) = 6.4 nM). Long-term treatment of schizophrenia with lurasidone has been shown to reduce the risk of relapse. Lurasidone appears associated with minimal effects on body weight and low risk for clinically meaningful alterations in glucose, lipids or electrocardiogram parameters."
    # query_ids = tokenizer(question)
    # document_ids = tokenizer(document)
    # document_ids2 = tokenizer(document2)
    # query_ids = torch.tensor(query_ids)
    # document_ids = torch.stack([torch.tensor(document_ids), torch.tensor(document_ids2)])
    # a = model(query_ids, document_ids)
    # print(a)

    # del document_ids
    # del a
    # gc.collect()
    # document_ids = tokenizer(document3)
    # document_ids2 = tokenizer(document4)
    # document_ids = torch.stack([torch.tensor(document_ids), torch.tensor(document_ids2)])
    # a = model(query_ids, document_ids)
    # print(a)

    end = time.time()
    print(f'Total execution time : {end-start}sec')



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
            with open("../documents/questions.jsonl", "r") as q:
                for line in q:
                    question = json.loads(line)
                    if question["query_id"] == query_id:
                        output["question"] = question["question"]
                        break

            output["retrieved_documents"] = [doc["id"] for doc in data["retrieved_documents"]]

            with open(outputFile, "a") as out:
                out.write(json.dumps(output) + "\n")