import torch

class CNNInteractionBasedModel(torch.nn.Module):
    def __init__(self, vocab_size, embedding_matrix, hidden_size=64):
        super().__init__()
        self.vocab_size = vocab_size
        self.embedding_layer = torch.nn.Embedding.from_pretrained(embedding_matrix, freeze=False) # Freeze = True because the layer is already trained

        self.conv = torch.nn.Conv2d(1, 32, (3, embedding_matrix.size(1)))  
        self.pool = torch.nn.MaxPool2d((3, 1))  

        self.global_pool = torch.nn.AdaptiveMaxPool2d((1, 1))
        
        self.activ = torch.nn.ReLU()
        
        self.fc1 = torch.nn.Linear(32, hidden_size)  
        self.fc2 = torch.nn.Linear(hidden_size, 1)  


    def forward(self, queries, documents):  
        query_embedd = self.embedding_layer(queries)
        document_embedd = self.embedding_layer(documents)
        interaction_matrix = torch.matmul(query_embedd, document_embedd.transpose(1, 2))
        interaction_matrix = interaction_matrix.unsqueeze(1)
        conv_output = self.conv(interaction_matrix)
        pooled_output = self.pool(conv_output)
        global_pooled_output = self.global_pool(pooled_output).squeeze()
        actived_output = self.activ(global_pooled_output)
        output = self.fc1(actived_output)
        output = self.fc2(output)
        prob = torch.sigmoid(output)
        return prob

