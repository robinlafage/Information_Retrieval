from tokenizer import Tokenizer
from CNNInteractionBasedModel import CNNInteractionBasedModel
from LoadingPreTrainedEmbeddings import LoadingPreTrainedEmbeddings
from SimpleDataset import SimpleDataset
import json

def main():
    medline = '../documents/easy_medline.jsonl'
    final_medline = ''
    with open(medline, 'r') as f :
        for doc in f :
            text = json.loads(doc)['text']
            final_medline = final_medline + ' ' + text
    
    questions = '../documents/easy_questions.jsonl'
    final_questions = ''
    with open(questions, 'r') as f :
        for doc in f :
            text = json.loads(doc)['question']
            final_questions = final_questions + ' ' + text


    tokenizer = Tokenizer()
    tokenizer.fit(final_questions, final_medline)

    # Exemple : charger un fichier
    loadingPreTrainedEmbeddings = LoadingPreTrainedEmbeddings()
    glove_file = "../glove/glove.6B.50d.txt"  # Chemin vers votre fichier .txt
    embeddings_index = loadingPreTrainedEmbeddings.load_glove_embeddings(glove_file)


    # Construire la matrice pour tous les mots de GloVe
    embedding_dim = 50  # Doit correspondre à la dimension choisie (par ex. 100d)
    vocab, embedding_matrix = loadingPreTrainedEmbeddings.create_glove_matrix(list(tokenizer.token_to_id.keys()),embeddings_index, embedding_dim)
    tokenizer.token_to_id = vocab
    
    model = CNNInteractionBasedModel(tokenizer.vocab_size, embedding_matrix)
    # query_ids = tokenizer(question)
    # document_ids = tokenizer(document)

    # print(f"Query tokens : {query_ids}")
    # print(f"Document tokens : {document_ids}")

    # if max(query_ids + document_ids) >= embedding_matrix.shape[0]:
    #     raise ValueError(f"Indice hors limite détecté. Max index : {max(query_ids + document_ids)}, Taille de la matrice d'embedding : {embedding_matrix.shape[0]}")


    # model(query_ids, document_ids)

    # query_ids2 = tokenizer(question2)
    # document_ids2 = tokenizer(document2)

    # model(query_ids2, document_ids2)

    print(tokenizer.vocab_size)
    print(tokenizer.token_to_id)
    ds = SimpleDataset("../documents/easy_questions.jsonl","../documents/questions_bm25_ranked.jsonl","../documents/easy_medline.jsonl", tokenizer)
    print(ds.__getitem__(0))

if __name__ == "__main__":
    main()