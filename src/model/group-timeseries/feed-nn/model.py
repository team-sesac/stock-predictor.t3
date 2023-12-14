import torch
import torch.nn as nn
from hyperparameter import HyperParameter

class FeedForwardNN(nn.Module):
    
    def __init__(self, num_continuous_features: int, num_categorical_features: list[int], hyper_parameter: HyperParameter):
        super(FeedForwardNN, self).__init__()
        
        self.embedding_dims = hyper_parameter.get_embedding_dims()
        self.hidden_units = hyper_parameter.get_hidden_units()
        self.drop_outs = hyper_parameter.get_drop_outs()

        # Embedding layers for categorical features
        self.embeddings = nn.ModuleList([
            nn.Embedding(num_categories, embedding_dim) for num_categories, embedding_dim in zip(num_categorical_features, self.embedding_dims)
        ])

        # Linear layer for continuous features
        self.linear_continuous = nn.Linear(num_continuous_features, self.hidden_units[0])
        self.linear_continuous_act = nn.ReLU()
        
        # Linear layer after concatenating continuous and flattened categorical features
        self.linear_concatenated = nn.Linear(num_continuous_features + sum(self.embedding_dims), self.hidden_units[1])
        self.linear_concatenated_act = nn.ReLU()
        
        # Additional hidden layers
        self.hidden_layers = nn.ModuleList([
            nn.Linear(self.hidden_units[i], self.hidden_units[i+1]) for i in range(1, len(self.hidden_units)-1)
        ])
        self.hidden_layer_acts = nn.ModuleList([ nn.ReLU() for _ in range(1, len(self.hidden_units)-1) ])

        # Output layer
        self.output_layer = nn.Linear(self.hidden_units[-1], 1)

        # Dropout layers
        self.dropout_layers = nn.ModuleList([
            nn.Dropout(dropout_rate) for dropout_rate in self.drop_outs
        ])

        # Batch normalization layers
        self.batch_norm_layers = nn.ModuleList([
            nn.BatchNorm1d(hidden_unit) for hidden_unit in self.hidden_units
        ])

    def forward(self, continuous, categorical):
        
        # Embedding categorical features
        embeddings = [ embedding(categorical[:, i].to(torch.int)) for i, embedding in enumerate(self.embeddings) ]
        flattened_embeddings = [ embedding.view(embedding.size(0), -1) for embedding in embeddings ]
        
        # Concatenate continuous and flattened categorical features
        concatenated = torch.cat([continuous] + flattened_embeddings, dim=1)
        
        # Apply linear transformation for continuous features
        x = self.linear_continuous_act(self.linear_continuous(continuous))
        
        # Apply linear transformation for concatenated features
        x = self.linear_concatenated_act(self.linear_concatenated(concatenated))
        
        # Apply batch normalization and dropout
        x = self.batch_norm_layers[0](x)
        
        # xx = self.dropout_layers[0](x)
        # x = F.dropout(x, p=self.dropout_layers[0], training=True)
        x = self.dropout_layers[0](x)
        
        # Apply hidden layers with batch normalization, ReLU, and dropout
        for layer, batch_norm, dropout, act in zip(self.hidden_layers, self.batch_norm_layers[1:], self.dropout_layers[1:], self.hidden_layer_acts):
            x = act(batch_norm(layer(x)))
            x = dropout(x)
            # x = F.dropout(x, p=dropout, training=True)
            
        # Output layer
        out = self.output_layer(x)

        return out
    
if __name__ == "__main__":
    
    a = nn.ModuleList([
        nn.Embedding(num_categories, embedding_dim) for num_categories, embedding_dim in zip([2], [20])
    ])
    t = torch.IntTensor([[0]])
    r = a[0](t)
    print(r)
    
    # data = torch.Tensor([[0.123, 0.321, 0.2, 0], [0.643, 0.6, 0.4, 1]])
    # hyper_parameter = HyperParameter(lr=0.1,
    #                                 epochs=100,
    #                                 hidden_units=[2, 2],
    #                                 embedding_dims=[3],
    #                                 drop_outs=[0.1, 0.2, 0.3])
    # model = FeedForwardNN(num_continuous_features=3, num_categorical_features=[2], hyper_parameter=hyper_parameter)
    # result = model(data[:, :-1], data[:, [-1]])
    # print(result)