import torch

class LoadingPreTrainedEmbeddings:
    def load_glove_embeddings(self, glove_file_path):
        embeddings_index = {}
        with open(glove_file_path, encoding='utf-8') as f:
            for line in f:
                values = line.split()
                word = values[0]
                vector = torch.tensor([float(v) for v in values[1:]], dtype=torch.float32)
                embeddings_index[word] = vector
        return embeddings_index

    def create_glove_matrix(self, words, embeddings_index, embedding_dim):
        # Liste des vecteurs d'embeddings pour les mots trouvés
        matrix = []
        vocab = {"<PAD>":0, "<UNK>":1}  # Dictionnaire des mots mappés à des indices
        zeroVector = torch.zeros(embedding_dim)
        
        for idx, word in enumerate(words):
            if word in embeddings_index:  # Vérifier si le mot est dans GloVe
                vocab[word] = idx  # Mapper chaque mot à son index
                matrix.append(embeddings_index[word])
            elif word not in ["<PAD>", "<UNK>"] : 
                vocab[word] = 1
                matrix.append(zeroVector)
            else :
                matrix.append(zeroVector)
                
        # Convertir en un tensor unique
        if matrix:
            matrix = torch.stack(matrix)  # Crée un tensor de dimension [len(words), embedding_dim]
        else:
            matrix = torch.empty((0, embedding_dim), dtype=torch.float32)  # Cas où aucun mot n'a d'embedding
        return vocab, matrix
    
    # def create_glove_matrix_from_all_words(embeddings_index, embedding_dim):
    #     vocab = {}  # Dictionnaire des mots mappés à des indices
    #     matrix = []  # Liste des vecteurs
        
    #     for idx, (word, vector) in enumerate(embeddings_index.items()):
    #         if word in embeddings_index:
    #             vocab[word] = idx  # Mapper chaque mot à son index
    #             matrix.append(vector)
    #         else : 
    #             print(f'Missing : {word}')
        
    #     if matrix:
    #         matrix = torch.stack(matrix)  # Crée un tensor de dimension [len(words), embedding_dim]
    #     else:
    #         matrix = torch.empty((0, embedding_dim), dtype=torch.float32)  # Cas où aucun mot n'a d'embedding
    #     return vocab, matrix