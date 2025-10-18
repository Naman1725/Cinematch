"""Script to download and process MovieLens dataset"""
import os
import zipfile
import requests
import pandas as pd
from pathlib import Path


def download_movielens(data_dir: str = "./data"):
    """
    Download MovieLens 25M dataset

    Args:
        data_dir: Directory to save the data
    """
    data_path = Path(data_dir)
    data_path.mkdir(parents=True, exist_ok=True)

    # MovieLens 25M dataset URL
    url = "https://files.grouplens.org/datasets/movielens/ml-25m.zip"
    zip_path = data_path / "ml-25m.zip"
    extract_path = data_path / "ml-25m"

    if extract_path.exists():
        print("Dataset already exists")
        return

    print("Downloading MovieLens 25M dataset...")
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))

    with open(zip_path, 'wb') as file:
        downloaded = 0
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                file.write(chunk)
                downloaded += len(chunk)
                progress = (downloaded / total_size) * 100
                print(f"\rProgress: {progress:.1f}%", end='')

    print("\n\nExtracting dataset...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(data_path)

    print("Cleaning up...")
    os.remove(zip_path)

    print("Dataset downloaded and extracted successfully!")


def process_movielens(data_dir: str = "./data"):
    """
    Process MovieLens dataset for training

    Args:
        data_dir: Directory containing the data
    """
    data_path = Path(data_dir) / "ml-25m"

    print("Loading ratings...")
    ratings = pd.read_csv(
        data_path / "ratings.csv",
        usecols=['userId', 'movieId', 'rating', 'timestamp']
    )

    print("Loading movies...")
    movies = pd.read_csv(
        data_path / "movies.csv",
        usecols=['movieId', 'title', 'genres']
    )

    print(f"Loaded {len(ratings)} ratings and {len(movies)} movies")

    # Filter movies with at least 50 ratings
    movie_counts = ratings['movieId'].value_counts()
    popular_movies = movie_counts[movie_counts >= 50].index
    ratings_filtered = ratings[ratings['movieId'].isin(popular_movies)]

    # Filter users with at least 20 ratings
    user_counts = ratings_filtered['userId'].value_counts()
    active_users = user_counts[user_counts >= 20].index
    ratings_filtered = ratings_filtered[ratings_filtered['userId'].isin(active_users)]

    print(f"After filtering: {len(ratings_filtered)} ratings")

    # Create user and movie ID mappings
    unique_users = ratings_filtered['userId'].unique()
    unique_movies = ratings_filtered['movieId'].unique()

    user_id_map = {old_id: new_id for new_id, old_id in enumerate(unique_users)}
    movie_id_map = {old_id: new_id for new_id, old_id in enumerate(unique_movies)}

    # Map IDs
    ratings_filtered['userId'] = ratings_filtered['userId'].map(user_id_map)
    ratings_filtered['movieId'] = ratings_filtered['movieId'].map(movie_id_map)

    # Save processed data
    processed_path = Path(data_dir) / "processed"
    processed_path.mkdir(exist_ok=True)

    ratings_filtered.to_csv(processed_path / "ratings.csv", index=False)
    movies[movies['movieId'].isin(movie_id_map.keys())].to_csv(
        processed_path / "movies.csv",
        index=False
    )

    # Save mappings
    pd.DataFrame(
        list(user_id_map.items()),
        columns=['original_id', 'mapped_id']
    ).to_csv(processed_path / "user_id_map.csv", index=False)

    pd.DataFrame(
        list(movie_id_map.items()),
        columns=['original_id', 'mapped_id']
    ).to_csv(processed_path / "movie_id_map.csv", index=False)

    print(f"\nProcessed data saved to {processed_path}")
    print(f"Number of users: {len(unique_users)}")
    print(f"Number of movies: {len(unique_movies)}")
    print(f"Sparsity: {(1 - len(ratings_filtered) / (len(unique_users) * len(unique_movies))) * 100:.2f}%")


if __name__ == "__main__":
    download_movielens()
    process_movielens()
