"""Training script for Neural Collaborative Filtering model"""
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, random_split
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple
from .model import NeuralCollaborativeFiltering
from tqdm import tqdm


class MovieLensDataset(Dataset):
    """MovieLens dataset for PyTorch"""

    def __init__(self, ratings_df: pd.DataFrame):
        """
        Initialize dataset

        Args:
            ratings_df: DataFrame with columns [userId, movieId, rating]
        """
        self.users = torch.LongTensor(ratings_df['userId'].values)
        self.movies = torch.LongTensor(ratings_df['movieId'].values)
        # Normalize ratings to 0-1 range for better training
        self.ratings = torch.FloatTensor(
            (ratings_df['rating'].values - 1) / 4
        )

    def __len__(self):
        return len(self.users)

    def __getitem__(self, idx):
        return self.users[idx], self.movies[idx], self.ratings[idx]


def train_epoch(
    model: nn.Module,
    train_loader: DataLoader,
    optimizer: optim.Optimizer,
    criterion: nn.Module,
    device: torch.device
) -> float:
    """
    Train for one epoch

    Args:
        model: NCF model
        train_loader: Training data loader
        optimizer: Optimizer
        criterion: Loss function
        device: Device to train on

    Returns:
        Average training loss
    """
    model.train()
    total_loss = 0
    num_batches = 0

    for users, movies, ratings in tqdm(train_loader, desc="Training"):
        users = users.to(device)
        movies = movies.to(device)
        ratings = ratings.to(device)

        # Forward pass
        predictions = model(users, movies)

        # Calculate loss
        loss = criterion(predictions, ratings)

        # Backward pass
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_loss += loss.item()
        num_batches += 1

    return total_loss / num_batches


def validate(
    model: nn.Module,
    val_loader: DataLoader,
    criterion: nn.Module,
    device: torch.device
) -> Tuple[float, float]:
    """
    Validate the model

    Args:
        model: NCF model
        val_loader: Validation data loader
        criterion: Loss function
        device: Device to validate on

    Returns:
        Tuple of (average loss, RMSE)
    """
    model.eval()
    total_loss = 0
    total_mse = 0
    num_batches = 0

    with torch.no_grad():
        for users, movies, ratings in tqdm(val_loader, desc="Validating"):
            users = users.to(device)
            movies = movies.to(device)
            ratings = ratings.to(device)

            # Forward pass
            predictions = model(users, movies)

            # Calculate loss
            loss = criterion(predictions, ratings)

            # Calculate MSE for RMSE
            mse = nn.MSELoss()(predictions, ratings)

            total_loss += loss.item()
            total_mse += mse.item()
            num_batches += 1

    avg_loss = total_loss / num_batches
    rmse = np.sqrt(total_mse / num_batches) * 4  # Scale back to 1-5 range

    return avg_loss, rmse


def train_model(
    data_dir: str = "./data/processed",
    model_dir: str = "./models",
    embedding_dim: int = 64,
    mlp_layers: list = [128, 64, 32],
    batch_size: int = 256,
    learning_rate: float = 0.001,
    num_epochs: int = 20,
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
):
    """
    Train the NCF model

    Args:
        data_dir: Directory containing processed data
        model_dir: Directory to save the model
        embedding_dim: Embedding dimension
        mlp_layers: MLP layer sizes
        batch_size: Batch size for training
        learning_rate: Learning rate
        num_epochs: Number of training epochs
        device: Device to train on
    """
    print(f"Using device: {device}")

    # Load data
    print("Loading data...")
    ratings_df = pd.read_csv(Path(data_dir) / "ratings.csv")

    # Get number of unique users and movies
    num_users = ratings_df['userId'].max() + 1
    num_movies = ratings_df['movieId'].max() + 1

    print(f"Number of users: {num_users}")
    print(f"Number of movies: {num_movies}")
    print(f"Number of ratings: {len(ratings_df)}")

    # Create dataset
    dataset = MovieLensDataset(ratings_df)

    # Split into train and validation
    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = random_split(
        dataset,
        [train_size, val_size],
        generator=torch.Generator().manual_seed(42)
    )

    # Create data loaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=4,
        pin_memory=True
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=4,
        pin_memory=True
    )

    # Create model
    print("\nInitializing model...")
    model = NeuralCollaborativeFiltering(
        num_users=num_users,
        num_items=num_movies,
        embedding_dim=embedding_dim,
        mlp_layers=mlp_layers,
        dropout=0.2
    ).to(device)

    print(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")

    # Loss and optimizer
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer,
        mode='min',
        factor=0.5,
        patience=2,
        verbose=True
    )

    # Training loop
    print("\nStarting training...")
    best_rmse = float('inf')

    for epoch in range(num_epochs):
        print(f"\nEpoch {epoch + 1}/{num_epochs}")

        # Train
        train_loss = train_epoch(model, train_loader, optimizer, criterion, device)

        # Validate
        val_loss, val_rmse = validate(model, val_loader, criterion, device)

        print(f"Train Loss: {train_loss:.4f}")
        print(f"Val Loss: {val_loss:.4f}, Val RMSE: {val_rmse:.4f}")

        # Learning rate scheduling
        scheduler.step(val_loss)

        # Save best model
        if val_rmse < best_rmse:
            best_rmse = val_rmse
            model_path = Path(model_dir)
            model_path.mkdir(parents=True, exist_ok=True)

            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'num_users': num_users,
                'num_movies': num_movies,
                'embedding_dim': embedding_dim,
                'mlp_layers': mlp_layers,
                'val_rmse': val_rmse,
            }, model_path / "ncf_model.pth")

            print(f"Model saved! Best RMSE: {best_rmse:.4f}")

    print("\nTraining completed!")
    print(f"Best validation RMSE: {best_rmse:.4f}")


if __name__ == "__main__":
    train_model()
