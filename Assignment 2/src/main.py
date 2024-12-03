from tokenizer import Tokenizer
from CNNInteractionBasedModel import CNNInteractionBasedModel
from LoadingPreTrainedEmbeddings import LoadingPreTrainedEmbeddings


def main():
    question = "Which name is also used to describe the Amazon rainforest in English?"
    document = "The Amazon rainforest, also known in English as Amazonia or the Amazon Jungle"

    question2 = "Which name is also used to describe the Amazon rainforest in English?"
    document2 = "The Amazon rainforest, also known in English as Amazonia or the Amazon Jungle forever and ever and ever"

    tokenizer = Tokenizer()
    tokenizer.fit(question, document)
    tokenizer.fit(question2, document2)

    # Exemple : charger un fichier
    loadingPreTrainedEmbeddings = LoadingPreTrainedEmbeddings()
    glove_file = "../glove.6B.50d.txt"  # Chemin vers votre fichier .txt
    embeddings_index = loadingPreTrainedEmbeddings.load_glove_embeddings(glove_file)


    # Construire la matrice pour tous les mots de GloVe
    embedding_dim = 50  # Doit correspondre à la dimension choisie (par ex. 100d)
    vocab, embedding_matrix = loadingPreTrainedEmbeddings.create_glove_matrix(list(tokenizer.token_to_id.keys()),embeddings_index, embedding_dim)
    tokenizer.token_to_id = vocab
    
    model = CNNInteractionBasedModel(tokenizer.vocab_size, embedding_matrix)
    query_ids = tokenizer(question)
    document_ids = tokenizer(document)

    print(f"Query tokens : {query_ids}")
    print(f"Document tokens : {document_ids}")

    if max(query_ids + document_ids) >= embedding_matrix.shape[0]:
        raise ValueError(f"Indice hors limite détecté. Max index : {max(query_ids + document_ids)}, Taille de la matrice d'embedding : {embedding_matrix.shape[0]}")


    model(query_ids, document_ids)

    query_ids2 = tokenizer(question2)
    document_ids2 = tokenizer(document2)

    model(query_ids2, document_ids2)

if __name__ == "__main__":
    main()