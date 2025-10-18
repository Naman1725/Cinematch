"""TMDB API Service"""
import httpx
from typing import Optional, List, Dict, Any
from app.core.config import settings
from fastapi import HTTPException


class TMDBService:
    """Service for interacting with The Movie Database API"""

    def __init__(self):
        self.api_key = settings.TMDB_API_KEY
        self.base_url = settings.TMDB_BASE_URL
        self.image_base_url = "https://image.tmdb.org/t/p"

    async def get_movie_details(self, tmdb_id: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed movie information from TMDB

        Args:
            tmdb_id: TMDB movie ID

        Returns:
            Movie details dictionary
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/movie/{tmdb_id}",
                    params={
                        "api_key": self.api_key,
                        "append_to_response": "credits,videos,keywords"
                    }
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                print(f"Error fetching movie {tmdb_id}: {e}")
                return None

    async def search_movies(
        self,
        query: str,
        page: int = 1,
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Search for movies on TMDB

        Args:
            query: Search query
            page: Page number
            year: Optional year filter

        Returns:
            Search results
        """
        params = {
            "api_key": self.api_key,
            "query": query,
            "page": page,
            "include_adult": False
        }

        if year:
            params["year"] = year

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/search/movie",
                    params=params
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                print(f"Error searching movies: {e}")
                return {"results": [], "total_pages": 0, "total_results": 0}

    async def get_popular_movies(self, page: int = 1) -> Dict[str, Any]:
        """
        Get popular movies from TMDB

        Args:
            page: Page number

        Returns:
            Popular movies
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/movie/popular",
                    params={"api_key": self.api_key, "page": page}
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                print(f"Error fetching popular movies: {e}")
                return {"results": [], "total_pages": 0, "total_results": 0}

    async def get_trending_movies(
        self,
        time_window: str = "week",
        page: int = 1
    ) -> Dict[str, Any]:
        """
        Get trending movies from TMDB

        Args:
            time_window: 'day' or 'week'
            page: Page number

        Returns:
            Trending movies
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/trending/movie/{time_window}",
                    params={"api_key": self.api_key, "page": page}
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                print(f"Error fetching trending movies: {e}")
                return {"results": [], "total_pages": 0, "total_results": 0}

    async def get_movie_videos(self, tmdb_id: int) -> List[Dict[str, Any]]:
        """
        Get movie trailers and videos

        Args:
            tmdb_id: TMDB movie ID

        Returns:
            List of videos
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/movie/{tmdb_id}/videos",
                    params={"api_key": self.api_key}
                )
                response.raise_for_status()
                data = response.json()
                return data.get("results", [])
            except httpx.HTTPError as e:
                print(f"Error fetching videos for movie {tmdb_id}: {e}")
                return []

    async def discover_movies(
        self,
        genre_ids: Optional[List[int]] = None,
        year: Optional[int] = None,
        sort_by: str = "popularity.desc",
        page: int = 1
    ) -> Dict[str, Any]:
        """
        Discover movies with filters

        Args:
            genre_ids: List of genre IDs
            year: Release year
            sort_by: Sort criterion
            page: Page number

        Returns:
            Discovered movies
        """
        params = {
            "api_key": self.api_key,
            "sort_by": sort_by,
            "page": page,
            "include_adult": False
        }

        if genre_ids:
            params["with_genres"] = ",".join(map(str, genre_ids))

        if year:
            params["year"] = year

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/discover/movie",
                    params=params
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                print(f"Error discovering movies: {e}")
                return {"results": [], "total_pages": 0, "total_results": 0}

    async def get_genres(self) -> List[Dict[str, Any]]:
        """
        Get list of movie genres

        Returns:
            List of genres
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/genre/movie/list",
                    params={"api_key": self.api_key}
                )
                response.raise_for_status()
                data = response.json()
                return data.get("genres", [])
            except httpx.HTTPError as e:
                print(f"Error fetching genres: {e}")
                return []

    def get_poster_url(self, poster_path: str, size: str = "w500") -> str:
        """
        Get full poster URL

        Args:
            poster_path: Poster path from TMDB
            size: Image size (w92, w154, w185, w342, w500, w780, original)

        Returns:
            Full poster URL
        """
        if not poster_path:
            return ""
        return f"{self.image_base_url}/{size}{poster_path}"

    def get_backdrop_url(self, backdrop_path: str, size: str = "w1280") -> str:
        """
        Get full backdrop URL

        Args:
            backdrop_path: Backdrop path from TMDB
            size: Image size (w300, w780, w1280, original)

        Returns:
            Full backdrop URL
        """
        if not backdrop_path:
            return ""
        return f"{self.image_base_url}/{size}{backdrop_path}"


# Global TMDB service instance
tmdb_service = TMDBService()
