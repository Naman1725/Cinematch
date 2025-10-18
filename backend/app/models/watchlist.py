"""Watchlist model"""
from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Watchlist(Base):
    """Watchlist model"""
    __tablename__ = "watchlist"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    movie_id = Column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), nullable=False)

    # Status
    is_favorite = Column(Boolean, default=False)
    watched = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="watchlist")
    movie = relationship("Movie", back_populates="watchlist")

    # Ensure a user can only have a movie once in watchlist
    __table_args__ = (
        UniqueConstraint('user_id', 'movie_id', name='unique_user_movie_watchlist'),
    )

    def __repr__(self):
        return f"<Watchlist user_id={self.user_id} movie_id={self.movie_id}>"
