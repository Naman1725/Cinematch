"""Rating schemas"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class RatingBase(BaseModel):
    """Base rating schema"""
    rating: float = Field(..., ge=0.5, le=5.0)


class RatingCreate(RatingBase):
    """Schema for creating a rating"""
    movie_id: int


class RatingUpdate(RatingBase):
    """Schema for updating a rating"""
    pass


class RatingResponse(BaseModel):
    """Schema for rating response"""
    id: int
    user_id: int
    movie_id: int
    rating: float
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
