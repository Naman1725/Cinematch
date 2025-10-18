# 🚀 Quick Start Guide

## Movie Recommendation System - Get Started in 5 Minutes!

This guide will get your movie recommendation system up and running quickly.

---

## Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- PostgreSQL 14 or higher (or use SQLite for testing)
- TMDB API Key ([Get it free here](https://www.themoviedb.org/settings/api))

---

## Step 1: Backend Setup (5 minutes)

### 1.1 Create Virtual Environment

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 1.2 Install Dependencies

```bash
pip install -r requirements.txt
```

### 1.3 Configure Environment

Create `backend/.env` file:

```env
# Quick Start Configuration (for local development)

# Database - Start with SQLite for quick testing
DATABASE_URL=sqlite:///./movie_recommendation.db

# Security - Generate a random secret key
SECRET_KEY=your-super-secret-key-change-this-in-production-12345
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# TMDB API - Get your key from https://www.themoviedb.org/settings/api
TMDB_API_KEY=your-tmdb-api-key-here
TMDB_BASE_URL=https://api.themoviedb.org/3

# Email (Optional for now - can configure later)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=noreply@movierecommendation.com

# Frontend URL
FRONTEND_URL=http://localhost:3000

# Environment
ENVIRONMENT=development
```

### 1.4 Initialize Database

```bash
# Initialize database tables
python -c "from app.core.database import init_db; init_db()"
```

### 1.5 Start Backend Server

```bash
uvicorn app.main:app --reload
```

✅ **Backend is running at http://localhost:8000**

Visit http://localhost:8000/docs to see the API documentation!

---

## Step 2: Test the Backend (2 minutes)

### Option A: Using Swagger UI

1. Open http://localhost:8000/docs
2. Try the `/api/auth/register` endpoint:
   - Click "Try it out"
   - Fill in:
     ```json
     {
       "email": "test@example.com",
       "username": "testuser",
       "password": "testpassword123",
       "full_name": "Test User"
     }
     ```
   - Click "Execute"
   - Copy the `access_token` from the response

3. Click "Authorize" button at the top
4. Paste your token: `Bearer your-access-token-here`
5. Now you can test all protected endpoints!

### Option B: Using curl

```bash
# Register a user
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "testpassword123",
    "full_name": "Test User"
  }'

# Login
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123"
  }'
```

---

## Step 3: Add Sample Movie Data (Optional)

Create a script `backend/add_sample_movies.py`:

```python
"""Add sample movies from TMDB"""
import asyncio
from app.core.database import SessionLocal
from app.services.tmdb import tmdb_service
from app.models.movie import Movie

async def add_popular_movies():
    db = SessionLocal()

    # Get popular movies from TMDB
    result = await tmdb_service.get_popular_movies()
    movies = result.get("results", [])[:20]  # Get first 20

    for movie_data in movies:
        # Get full movie details
        details = await tmdb_service.get_movie_details(movie_data["id"])

        if not details:
            continue

        # Check if movie already exists
        existing = db.query(Movie).filter(Movie.tmdb_id == details["id"]).first()
        if existing:
            print(f"Skipping {details['title']} - already exists")
            continue

        # Extract data
        release_year = None
        if details.get("release_date"):
            try:
                release_year = int(details["release_date"][:4])
            except:
                pass

        # Create movie
        movie = Movie(
            tmdb_id=details["id"],
            title=details["title"],
            original_title=details.get("original_title"),
            overview=details.get("overview"),
            tagline=details.get("tagline"),
            release_date=details.get("release_date"),
            release_year=release_year,
            poster_path=details.get("poster_path"),
            backdrop_path=details.get("backdrop_path"),
            vote_average=details.get("vote_average", 0),
            vote_count=details.get("vote_count", 0),
            popularity=details.get("popularity", 0),
            runtime=details.get("runtime"),
            budget=details.get("budget"),
            revenue=details.get("revenue"),
            status=details.get("status"),
            genres=[g["name"] for g in details.get("genres", [])],
            genres_ids=[g["id"] for g in details.get("genres", [])],
            languages=[lang["english_name"] for lang in details.get("spoken_languages", [])],
            adult=details.get("adult", False),
            original_language=details.get("original_language"),
        )

        db.add(movie)
        print(f"Added: {movie.title}")

    db.commit()
    db.close()
    print("\n✅ Sample movies added successfully!")

if __name__ == "__main__":
    asyncio.run(add_popular_movies())
```

Run it:

```bash
python add_sample_movies.py
```

---

## Step 4: Frontend Setup (Coming Soon)

The backend is fully functional! For the frontend, you have two options:

### Option A: Wait for Full Implementation
The frontend implementation is in progress and will include:
- Next.js 15 with App Router
- Professional UI with Tailwind CSS
- Dark/Light mode
- OAuth authentication
- All features listed in README

### Option B: Build Your Own Frontend
You can start building the frontend immediately using the API:

- API Documentation: http://localhost:8000/docs
- All endpoints are ready to use
- Authentication uses JWT tokens
- CORS is configured for http://localhost:3000

---

## 🎯 What's Working Right Now

✅ **User Authentication**
- Register new users
- Login with email/password
- JWT token-based authentication
- OAuth ready (Google, GitHub)

✅ **Database**
- User management
- Movie storage
- Ratings system
- Reviews system
- Watchlist functionality

✅ **Machine Learning** (when trained)
- Neural Collaborative Filtering model
- Personalized recommendations
- Similar movies suggestions

✅ **TMDB Integration**
- Search movies
- Get movie details
- Trending movies
- Popular movies

✅ **API Endpoints**
- `/api/auth/*` - Authentication
- `/api/movies/*` - Movie operations
- `/api/ratings/*` - User ratings
- `/api/reviews/*` - Movie reviews
- `/api/recommendations/*` - ML recommendations
- `/api/watchlist/*` - User watchlist

---

## 🔧 Configuration Options

### Use PostgreSQL Instead of SQLite

1. Install PostgreSQL
2. Create database:
   ```sql
   CREATE DATABASE movie_recommendation_db;
   ```
3. Update `.env`:
   ```env
   DATABASE_URL=postgresql://username:password@localhost:5432/movie_recommendation_db
   ```
4. Reinitialize:
   ```bash
   python -c "from app.core.database import init_db; init_db()"
   ```

### Train ML Model (Optional - takes 30-60 minutes)

```bash
# Download MovieLens dataset (250MB+)
python -m app.ml.download_data

# Train the model (requires GPU for speed, works on CPU too)
python -m app.ml.train
```

**Note:** The recommendation system works without training by falling back to popular movies.

---

## 📊 Testing the Full Flow

1. **Register a user**
   ```bash
   POST /api/auth/register
   ```

2. **Add some movies** (run the sample script above)

3. **Rate some movies**
   ```bash
   POST /api/ratings/
   {
     "movie_id": 1,
     "rating": 4.5
   }
   ```

4. **Get recommendations**
   ```bash
   GET /api/recommendations/
   ```

5. **Add to watchlist**
   ```bash
   POST /api/watchlist/
   {
     "movie_id": 1,
     "is_favorite": true
   }
   ```

---

## 🐛 Troubleshooting

### "Module not found" error
```bash
pip install -r requirements.txt
```

### Database connection error
- Check your `DATABASE_URL` in `.env`
- For SQLite, just use: `sqlite:///./movie_recommendation.db`

### TMDB API not working
- Get API key from https://www.themoviedb.org/settings/api
- Add it to `.env` as `TMDB_API_KEY`

### Port already in use
```bash
# Use a different port
uvicorn app.main:app --reload --port 8001
```

---

## 📚 Next Steps

1. ✅ Backend is running
2. 📝 Add sample movies
3. 🎨 Build or wait for frontend
4. 🤖 Train ML model (optional)
5. 🚀 Deploy to Render

---

## 🆘 Need Help?

- Check API docs: http://localhost:8000/docs
- Read full guide: [IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md)
- Check README: [README.md](./README.md)

---

## 🎉 Success!

Your movie recommendation backend is now running! You can:

- Register users
- Add movies from TMDB
- Rate movies
- Get recommendations
- Manage watchlists

The API is production-ready and waiting for a beautiful frontend! 🎬
