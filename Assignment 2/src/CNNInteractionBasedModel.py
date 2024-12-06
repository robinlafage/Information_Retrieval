import torch

class CNNInteractionBasedModel(torch.nn.Module):
    def __init__(self, vocab_size, embedding_matrix):
        super().__init__()
        self.vocab_size = vocab_size
        self.embedding_layer = torch.nn.Embedding.from_pretrained(embedding_matrix, freeze=True) # Freeze = True because the layer is already trained
        self.conv = torch.nn.Conv2d(1, 32, 3)  # Conv2D: input channels = 1, output channels = 32, kernel_size = 3
        self.pool = torch.nn.MaxPool2d(3)      # Pooling with kernel size = 3
        self.global_pool = torch.nn.AdaptiveMaxPool2d((1, 1))  # Global Max Pooling to reduce to fixed size
        self.activ = torch.nn.ReLU()
        self.lin = torch.nn.Linear(32, 1)  # Fixed size after global pooling

    def forward(self, query, document):
        # print("question ids:", query)
        # print("document ids:", document)

        query_tensor = torch.tensor(query).unsqueeze(0)  # Shape: [1, seq_len]
        document_tensor = torch.tensor(document).unsqueeze(0)

        query_embedd = self.embedding_layer(query_tensor).unsqueeze(1)  # Shape: [1, 1, seq_len, embedding_dim]
        document_embedd = self.embedding_layer(document_tensor).unsqueeze(1)

        query_conv = self.conv(query_embedd)
        document_conv = self.conv(document_embedd)

        query_pool = self.pool(query_conv)
        document_pool = self.pool(document_conv)

        query_global_pool = self.global_pool(query_pool).squeeze()  # Reduce to shape: [32]
        document_global_pool = self.global_pool(document_pool).squeeze()

        query_activ = self.activ(query_global_pool)
        document_activ = self.activ(document_global_pool)

        query_lin = self.lin(query_activ)
        document_lin = self.lin(document_activ)

        query_lin = query_lin.squeeze()
        document_lin = document_lin.squeeze()

        prob = torch.sigmoid(query_lin + document_lin)
        print("prob:", prob)

        return prob
