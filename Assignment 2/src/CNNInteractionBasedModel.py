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

    def forward(self, queries, documents):  
        
        query_embedd = self.embedding_layer(queries)
        document_embedd = self.embedding_layer(documents)

        interaction_matrix = torch.matmul(
            query_embedd,
            document_embedd.transpose(1, 2) 
        )

        interaction_matrix = interaction_matrix.unsqueeze(1)

        conv_output = self.conv(interaction_matrix)
        pooled_output = self.pool(conv_output)
        global_pooled_output = self.global_pool(pooled_output).squeeze()
        actived_ouput = self.activ(global_pooled_output)
        output = self.lin(actived_ouput).squeeze()

        prob = torch.sigmoid(output)

        return prob

