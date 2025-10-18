"""Pydantic schemas for request/response validation"""
from .user import (
    UserCreate, UserLogin, UserResponse, UserUpdate,
    Token, TokenPayload, PasswordReset, PasswordResetConfirm
)
from .movie import MovieResponse, MovieCreate, MovieUpdate, MovieFilter
from .rating import RatingCreate, RatingResponse, RatingUpdate
from .review import ReviewCreate, ReviewResponse, ReviewUpdate
from .watchlist import WatchlistCreate, WatchlistResponse

__all__ = [
    "UserCreate", "UserLogin", "UserResponse", "UserUpdate",
    "Token", "TokenPayload", "PasswordReset", "PasswordResetConfirm",
    "MovieResponse", "MovieCreate", "MovieUpdate", "MovieFilter",
    "RatingCreate", "RatingResponse", "RatingUpdate",
    "ReviewCreate", "ReviewResponse", "ReviewUpdate",
    "WatchlistCreate", "WatchlistResponse",
]
