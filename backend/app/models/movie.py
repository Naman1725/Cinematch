"""Movie model"""
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Movie(Base):
    """Movie model"""
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    tmdb_id = Column(Integer, unique=True, index=True, nullable=False)

    # Basic Information
    title = Column(String, index=True, nullable=False)
    original_title = Column(String, nullable=True)
    overview = Column(Text, nullable=True)
    tagline = Column(String, nullable=True)

    # Release Information
    release_date = Column(String, nullable=True)
    release_year = Column(Integer, index=True, nullable=True)

    # Media
    poster_path = Column(String, nullable=True)
    backdrop_path = Column(String, nullable=True)
    trailer_url = Column(String, nullable=True)

    # Ratings and Popularity
    vote_average = Column(Float, default=0.0)
    vote_count = Column(Integer, default=0)
    popularity = Column(Float, default=0.0)

    # Our own rating system
    avg_rating = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)

    # Details
    runtime = Column(Integer, nullable=True)  # in minutes
    budget = Column(Integer, nullable=True)
    revenue = Column(Integer, nullable=True)
    status = Column(String, nullable=True)  # Released, In Production, etc.

    # Categorical Data (stored as JSON)
    genres = Column(JSON, default=list)  # List of genre names
    genres_ids = Column(JSON, default=list)  # List of genre IDs
    languages = Column(JSON, default=list)  # Spoken languages
    production_countries = Column(JSON, default=list)
    production_companies = Column(JSON, default=list)

    # Cast and Crew (top 10)
    cast = Column(JSON, default=list)
    crew = Column(JSON, default=list)
    director = Column(String, nullable=True)

    # Content
    adult = Column(Boolean, default=False)
    original_language = Column(String, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_synced = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    ratings = relationship("Rating", back_populates="movie", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="movie", cascade="all, delete-orphan")
    watchlist = relationship("Watchlist", back_populates="movie", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Movie {self.title} ({self.release_year})>"
