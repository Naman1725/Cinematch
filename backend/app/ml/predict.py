"""Prediction and recommendation utilities"""
import torch
import numpy as np
from typing import List, Tuple, Optional
from pathlib import Path
from .model import NeuralCollaborativeFiltering
from sqlalchemy.orm import Session
from app.models.rating import Rating
from app.models.movie import Movie
from app.core.config import settings


class RecommendationEngine:
    """Recommendation engine using trained NCF model"""

    def __init__(self, model_path: str = None):
        """
        Initialize recommendation engine

        Args:
            model_path: Path to trained model checkpoint
        """
        if model_path is None:
            model_path = settings.MODEL_PATH

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.num_users = 0
        self.num_movies = 0

        if Path(model_path).exists():
            self.load_model(model_path)
        else:
            print(f"Warning: Model not found at {model_path}")

    def load_model(self, model_path: str):
        """
        Load trained model

        Args:
            model_path: Path to model checkpoint
        """
        print(f"Loading model from {model_path}...")
        checkpoint = torch.load(model_path, map_location=self.device)

        self.num_users = checkpoint['num_users']
        self.num_movies = checkpoint['num_movies']

        self.model = NeuralCollaborativeFiltering(
            num_users=self.num_users,
            num_items=self.num_movies,
            embedding_dim=checkpoint['embedding_dim'],
            mlp_layers=checkpoint['mlp_layers']
        ).to(self.device)

        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model.eval()

        print(f"Model loaded successfully! (RMSE: {checkpoint['val_rmse']:.4f})")

    def predict_rating(
        self,
        user_id: int,
        movie_id: int
    ) -> float:
        """
        Predict rating for a user-movie pair

        Args:
            user_id: User ID
            movie_id: Movie ID

        Returns:
            Predicted rating (1-5)
        """
        if self.model is None:
            return 3.0  # Default rating if model not loaded

        user_tensor = torch.LongTensor([user_id]).to(self.device)
        movie_tensor = torch.LongTensor([movie_id]).to(self.device)

        with torch.no_grad():
            prediction = self.model.predict(user_tensor, movie_tensor)

        return float(prediction[0])

    def get_user_recommendations(
        self,
        user_id: int,
        db: Session,
        top_k: int = 20,
        exclude_rated: bool = True
    ) -> List[Tuple[int, float]]:
        """
        Get top-k movie recommendations for a user

        Args:
            user_id: User ID
            db: Database session
            top_k: Number of recommendations
            exclude_rated: Whether to exclude already rated movies

        Returns:
            List of (movie_id, predicted_rating) tuples
        """
        if self.model is None:
            # Fallback to popular movies
            return self._get_popular_movies(db, top_k)

        # Get movies already rated by user
        exclude_movies = []
        if exclude_rated:
            rated_movies = db.query(Rating.movie_id).filter(
                Rating.user_id == user_id
            ).all()
            exclude_movies = [m[0] for m in rated_movies]

        # Get all movie IDs
        all_movies = db.query(Movie.id).filter(
            Movie.id.notin_(exclude_movies) if exclude_movies else True
        ).limit(1000).all()  # Limit for performance

        movie_ids = [m[0] for m in all_movies]

        if not movie_ids:
            return []

        # Predict ratings for all movies
        user_tensor = torch.LongTensor([user_id] * len(movie_ids)).to(self.device)
        movie_tensor = torch.LongTensor(movie_ids).to(self.device)

        with torch.no_grad():
            predictions = self.model.predict(user_tensor, movie_tensor)

        # Sort by predicted rating
        recommendations = list(zip(movie_ids, predictions))
        recommendations.sort(key=lambda x: x[1], reverse=True)

        return recommendations[:top_k]

    def get_similar_movies(
        self,
        movie_id: int,
        db: Session,
        top_k: int = 10
    ) -> List[Tuple[int, float]]:
        """
        Find similar movies based on item embeddings

        Args:
            movie_id: Movie ID
            db: Database session
            top_k: Number of similar movies to return

        Returns:
            List of (movie_id, similarity_score) tuples
        """
        if self.model is None:
            return []

        # Get movie embedding
        movie_tensor = torch.LongTensor([movie_id]).to(self.device)
        target_embedding = self.model.item_embedding_gmf(movie_tensor)

        # Get all movie IDs
        all_movies = db.query(Movie.id).filter(
            Movie.id != movie_id
        ).limit(1000).all()

        movie_ids = [m[0] for m in all_movies]

        if not movie_ids:
            return []

        # Get embeddings for all movies
        movies_tensor = torch.LongTensor(movie_ids).to(self.device)
        movies_embeddings = self.model.item_embedding_gmf(movies_tensor)

        # Calculate cosine similarity
        with torch.no_grad():
            similarities = torch.nn.functional.cosine_similarity(
                target_embedding,
                movies_embeddings
            )

        # Sort by similarity
        similarities = similarities.cpu().numpy()
        similar_movies = list(zip(movie_ids, similarities))
        similar_movies.sort(key=lambda x: x[1], reverse=True)

        return similar_movies[:top_k]

    def _get_popular_movies(
        self,
        db: Session,
        top_k: int = 20
    ) -> List[Tuple[int, float]]:
        """
        Fallback: Get popular movies based on average rating

        Args:
            db: Database session
            top_k: Number of movies to return

        Returns:
            List of (movie_id, avg_rating) tuples
        """
        popular_movies = db.query(
            Movie.id,
            Movie.avg_rating
        ).filter(
            Movie.rating_count >= 10
        ).order_by(
            Movie.avg_rating.desc(),
            Movie.rating_count.desc()
        ).limit(top_k).all()

        return [(m[0], m[1]) for m in popular_movies]


# Global recommendation engine instance
recommendation_engine = RecommendationEngine()
