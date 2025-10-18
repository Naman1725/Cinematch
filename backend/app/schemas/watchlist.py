"""Watchlist schemas"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class WatchlistBase(BaseModel):
    """Base watchlist schema"""
    movie_id: int


class WatchlistCreate(WatchlistBase):
    """Schema for creating a watchlist entry"""
    is_favorite: bool = False
    watched: bool = False


class WatchlistUpdate(BaseModel):
    """Schema for updating a watchlist entry"""
    is_favorite: Optional[bool] = None
    watched: Optional[bool] = None


class WatchlistResponse(BaseModel):
    """Schema for watchlist response"""
    id: int
    user_id: int
    movie_id: int
    is_favorite: bool
    watched: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
