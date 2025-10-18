"""Neural Collaborative Filtering Model"""
import torch
import torch.nn as nn
import numpy as np
from typing import Tuple, List


class NeuralCollaborativeFiltering(nn.Module):
    """
    Neural Collaborative Filtering (NCF) model
    Combines Matrix Factorization and Multi-Layer Perceptron
    for movie recommendations
    """

    def __init__(
        self,
        num_users: int,
        num_items: int,
        embedding_dim: int = 64,
        mlp_layers: List[int] = [128, 64, 32],
        dropout: float = 0.2
    ):
        """
        Initialize NCF model

        Args:
            num_users: Number of unique users
            num_items: Number of unique items (movies)
            embedding_dim: Dimension of embedding vectors
            mlp_layers: List of hidden layer sizes for MLP
            dropout: Dropout rate
        """
        super(NeuralCollaborativeFiltering, self).__init__()

        self.num_users = num_users
        self.num_items = num_items
        self.embedding_dim = embedding_dim

        # GMF (Generalized Matrix Factorization) embeddings
        self.user_embedding_gmf = nn.Embedding(num_users, embedding_dim)
        self.item_embedding_gmf = nn.Embedding(num_items, embedding_dim)

        # MLP embeddings
        self.user_embedding_mlp = nn.Embedding(num_users, embedding_dim)
        self.item_embedding_mlp = nn.Embedding(num_items, embedding_dim)

        # MLP layers
        mlp_modules = []
        input_size = embedding_dim * 2

        for layer_size in mlp_layers:
            mlp_modules.append(nn.Linear(input_size, layer_size))
            mlp_modules.append(nn.ReLU())
            mlp_modules.append(nn.Dropout(dropout))
            input_size = layer_size

        self.mlp = nn.Sequential(*mlp_modules)

        # Final prediction layer
        self.predict_layer = nn.Linear(
            embedding_dim + mlp_layers[-1],
            1
        )

        # Initialize weights
        self._init_weights()

    def _init_weights(self):
        """Initialize model weights"""
        nn.init.normal_(self.user_embedding_gmf.weight, std=0.01)
        nn.init.normal_(self.item_embedding_gmf.weight, std=0.01)
        nn.init.normal_(self.user_embedding_mlp.weight, std=0.01)
        nn.init.normal_(self.item_embedding_mlp.weight, std=0.01)

        for m in self.mlp:
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)

        nn.init.xavier_uniform_(self.predict_layer.weight)

    def forward(
        self,
        user_indices: torch.Tensor,
        item_indices: torch.Tensor
    ) -> torch.Tensor:
        """
        Forward pass

        Args:
            user_indices: Tensor of user indices
            item_indices: Tensor of item indices

        Returns:
            Predicted ratings
        """
        # GMF part
        user_emb_gmf = self.user_embedding_gmf(user_indices)
        item_emb_gmf = self.item_embedding_gmf(item_indices)
        gmf_output = user_emb_gmf * item_emb_gmf

        # MLP part
        user_emb_mlp = self.user_embedding_mlp(user_indices)
        item_emb_mlp = self.item_embedding_mlp(item_indices)
        mlp_input = torch.cat([user_emb_mlp, item_emb_mlp], dim=-1)
        mlp_output = self.mlp(mlp_input)

        # Concatenate GMF and MLP outputs
        concat = torch.cat([gmf_output, mlp_output], dim=-1)

        # Final prediction
        prediction = self.predict_layer(concat)

        return prediction.squeeze()

    def predict(
        self,
        user_indices: torch.Tensor,
        item_indices: torch.Tensor
    ) -> np.ndarray:
        """
        Make predictions (scaled to 1-5 rating)

        Args:
            user_indices: Tensor of user indices
            item_indices: Tensor of item indices

        Returns:
            Predicted ratings as numpy array
        """
        self.eval()
        with torch.no_grad():
            predictions = self.forward(user_indices, item_indices)
            # Scale predictions to 1-5 range
            predictions = torch.sigmoid(predictions) * 4 + 1

        return predictions.cpu().numpy()

    def recommend_for_user(
        self,
        user_id: int,
        num_items: int,
        top_k: int = 10,
        exclude_items: List[int] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate top-k recommendations for a user

        Args:
            user_id: User ID
            num_items: Total number of items
            top_k: Number of recommendations to return
            exclude_items: List of item IDs to exclude (already rated)

        Returns:
            Tuple of (item_ids, scores)
        """
        self.eval()

        # Create user and item tensors
        user_tensor = torch.LongTensor([user_id] * num_items)
        item_tensor = torch.LongTensor(list(range(num_items)))

        # Get predictions
        with torch.no_grad():
            scores = self.predict(user_tensor, item_tensor)

        # Exclude already rated items
        if exclude_items:
            scores[exclude_items] = -np.inf

        # Get top-k items
        top_indices = np.argsort(scores)[::-1][:top_k]
        top_scores = scores[top_indices]

        return top_indices, top_scores


class ContentEnhancedNCF(NeuralCollaborativeFiltering):
    """
    Enhanced NCF model with content features (genres, year, etc.)
    """

    def __init__(
        self,
        num_users: int,
        num_items: int,
        num_genres: int,
        embedding_dim: int = 64,
        mlp_layers: List[int] = [128, 64, 32],
        dropout: float = 0.2
    ):
        """
        Initialize Content-Enhanced NCF model

        Args:
            num_users: Number of unique users
            num_items: Number of unique items
            num_genres: Number of unique genres
            embedding_dim: Dimension of embedding vectors
            mlp_layers: List of hidden layer sizes
            dropout: Dropout rate
        """
        super().__init__(num_users, num_items, embedding_dim, mlp_layers, dropout)

        # Genre embedding
        self.genre_embedding = nn.Embedding(num_genres, embedding_dim // 2)

        # Update MLP to accommodate genre features
        mlp_modules = []
        input_size = embedding_dim * 2 + (embedding_dim // 2)

        for layer_size in mlp_layers:
            mlp_modules.append(nn.Linear(input_size, layer_size))
            mlp_modules.append(nn.ReLU())
            mlp_modules.append(nn.Dropout(dropout))
            input_size = layer_size

        self.mlp = nn.Sequential(*mlp_modules)

    def forward(
        self,
        user_indices: torch.Tensor,
        item_indices: torch.Tensor,
        genre_indices: torch.Tensor = None
    ) -> torch.Tensor:
        """
        Forward pass with content features

        Args:
            user_indices: User indices
            item_indices: Item indices
            genre_indices: Genre indices (optional)

        Returns:
            Predicted ratings
        """
        # GMF part
        user_emb_gmf = self.user_embedding_gmf(user_indices)
        item_emb_gmf = self.item_embedding_gmf(item_indices)
        gmf_output = user_emb_gmf * item_emb_gmf

        # MLP part
        user_emb_mlp = self.user_embedding_mlp(user_indices)
        item_emb_mlp = self.item_embedding_mlp(item_indices)

        if genre_indices is not None:
            genre_emb = self.genre_embedding(genre_indices)
            mlp_input = torch.cat([user_emb_mlp, item_emb_mlp, genre_emb], dim=-1)
        else:
            mlp_input = torch.cat([user_emb_mlp, item_emb_mlp], dim=-1)

        mlp_output = self.mlp(mlp_input)

        # Concatenate and predict
        concat = torch.cat([gmf_output, mlp_output], dim=-1)
        prediction = self.predict_layer(concat)

        return prediction.squeeze()
