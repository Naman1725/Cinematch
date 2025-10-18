"""Movie schemas"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class MovieBase(BaseModel):
    """Base movie schema"""
    tmdb_id: int
    title: str
    overview: Optional[str] = None


class MovieCreate(MovieBase):
    """Schema for creating a movie"""
    original_title: Optional[str] = None
    tagline: Optional[str] = None
    release_date: Optional[str] = None
    release_year: Optional[int] = None
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None
    trailer_url: Optional[str] = None
    vote_average: float = 0.0
    vote_count: int = 0
    popularity: float = 0.0
    runtime: Optional[int] = None
    budget: Optional[int] = None
    revenue: Optional[int] = None
    status: Optional[str] = None
    genres: List[str] = []
    genres_ids: List[int] = []
    languages: List[str] = []
    production_countries: List[str] = []
    production_companies: List[str] = []
    cast: List[dict] = []
    crew: List[dict] = []
    director: Optional[str] = None
    adult: bool = False
    original_language: Optional[str] = None


class MovieUpdate(BaseModel):
    """Schema for updating a movie"""
    title: Optional[str] = None
    overview: Optional[str] = None
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None
    trailer_url: Optional[str] = None
    avg_rating: Optional[float] = None
    rating_count: Optional[int] = None


class MovieResponse(BaseModel):
    """Schema for movie response"""
    id: int
    tmdb_id: int
    title: str
    original_title: Optional[str] = None
    overview: Optional[str] = None
    tagline: Optional[str] = None
    release_date: Optional[str] = None
    release_year: Optional[int] = None
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None
    trailer_url: Optional[str] = None
    vote_average: float
    vote_count: int
    popularity: float
    avg_rating: float
    rating_count: int
    runtime: Optional[int] = None
    budget: Optional[int] = None
    revenue: Optional[int] = None
    status: Optional[str] = None
    genres: List[str]
    genres_ids: List[int]
    languages: List[str]
    production_countries: List[str]
    production_companies: List[str]
    cast: List[dict]
    crew: List[dict]
    director: Optional[str] = None
    adult: bool
    original_language: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MovieFilter(BaseModel):
    """Schema for filtering movies"""
    search: Optional[str] = None
    genres: Optional[List[str]] = None
    year_min: Optional[int] = None
    year_max: Optional[int] = None
    rating_min: Optional[float] = None
    rating_max: Optional[float] = None
    language: Optional[str] = None
    sort_by: Optional[str] = "popularity"  # popularity, rating, release_date, title
    order: Optional[str] = "desc"  # asc or desc
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
