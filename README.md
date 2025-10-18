# 🎬 AI-Powered Movie Recommendation System

A production-ready, full-stack movie recommendation system powered by Deep Learning (Neural Collaborative Filtering) with a modern, professional UI.

## ✨ Features

### 🤖 AI-Powered Recommendations
- **Neural Collaborative Filtering** using PyTorch
- Hybrid approach (collaborative + content-based filtering)
- Personalized recommendations based on user preferences
- Similar movies suggestions
- Trending and popular movies

### 🔐 Advanced Authentication
- Email/Password authentication with JWT
- OAuth 2.0 (Google & GitHub)
- Password reset via email
- Email verification
- Secure session management

### 🎥 Movie Features
- Advanced search with filters (genre, year, rating, language)
- Detailed movie information (posters, trailers, cast, synopsis)
- User ratings (1-5 stars)
- Reviews and comments
- Personal watchlist/favorites
- Watch history tracking

### 🎨 Modern UI/UX
- Unique, professional design
- Dark/Light mode toggle
- Fully responsive (mobile, tablet, desktop)
- Smooth animations with Framer Motion
- Infinite scroll
- Search autocomplete
- Loading skeletons

### 🌐 Additional Features
- Multi-language support (i18n)
- Email notifications
- User dashboard with statistics
- Admin panel
- Social features (share, like reviews)
- Export functionality

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern, high-performance Python web framework
- **PyTorch** - Deep learning framework for recommendation engine
- **PostgreSQL** - Reliable, scalable database
- **SQLAlchemy** - ORM for database management
- **Pydantic** - Data validation
- **JWT** - Secure authentication

### Frontend
- **Next.js 15** - React framework with SSR
- **React 19** - UI library
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first CSS framework
- **Framer Motion** - Animation library
- **NextAuth.js** - Authentication for Next.js
- **React Query** - Data fetching and caching

### ML & Data
- **PyTorch** - Neural network implementation
- **Pandas & NumPy** - Data processing
- **Scikit-learn** - ML utilities
- **MovieLens Dataset** - Training data
- **TMDB API** - Real-time movie information

## 📁 Project Structure

```
movie_recommendation/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── auth.py
│   │   │   │   ├── movies.py
│   │   │   │   ├── recommendations.py
│   │   │   │   ├── ratings.py
│   │   │   │   └── users.py
│   │   │   └── deps.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── database.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── movie.py
│   │   │   ├── rating.py
│   │   │   └── review.py
│   │   ├── schemas/
│   │   │   └── ...
│   │   ├── ml/
│   │   │   ├── model.py
│   │   │   ├── train.py
│   │   │   └── predict.py
│   │   └── main.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── app/
│   │   ├── (auth)/
│   │   │   ├── login/
│   │   │   └── register/
│   │   ├── (main)/
│   │   │   ├── page.tsx
│   │   │   ├── movies/
│   │   │   ├── profile/
│   │   │   ├── watchlist/
│   │   │   └── admin/
│   │   └── api/auth/
│   ├── components/
│   │   ├── ui/
│   │   ├── MovieCard.tsx
│   │   ├── Navbar.tsx
│   │   └── ...
│   ├── lib/
│   ├── styles/
│   ├── public/
│   ├── package.json
│   └── .env.local.example
└── README.md
```

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- TMDB API Key

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Setup environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run database migrations:
```bash
alembic upgrade head
```

6. Download and process MovieLens dataset:
```bash
python -m app.ml.download_data
```

7. Train the ML model:
```bash
python -m app.ml.train
```

8. Start the server:
```bash
uvicorn app.main:app --reload
```

Backend will run at `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Setup environment variables:
```bash
cp .env.local.example .env.local
# Edit .env.local with your configuration
```

4. Start development server:
```bash
npm run dev
```

Frontend will run at `http://localhost:3000`

## 🔑 Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://user:password@localhost:5432/movie_db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
TMDB_API_KEY=your-tmdb-api-key
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FRONTEND_URL=http://localhost:3000
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-nextauth-secret
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
```

## 🌐 API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🎯 Key Endpoints

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/movies` - Get movies with filters
- `GET /api/movies/{id}` - Get movie details
- `POST /api/ratings` - Rate a movie
- `GET /api/recommendations` - Get personalized recommendations
- `GET /api/recommendations/similar/{movie_id}` - Get similar movies

## 🔧 Deployment (Render)

### Backend Deployment

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set build command: `pip install -r backend/requirements.txt`
4. Set start command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables from `.env.example`
6. Create a PostgreSQL database on Render and link it

### Frontend Deployment

1. Create a new Static Site on Render
2. Set build command: `cd frontend && npm install && npm run build`
3. Set publish directory: `frontend/out`
4. Add environment variables from `.env.local.example`

## 📊 ML Model Details

The recommendation system uses **Neural Collaborative Filtering (NCF)** which combines:

1. **Matrix Factorization**: Learns user and item embeddings
2. **Multi-Layer Perceptron**: Captures non-linear user-item interactions
3. **Hybrid Features**: Incorporates movie metadata (genres, year, popularity)

### Model Architecture
```
User ID → Embedding → |
                       | → Concatenate → Dense Layers → Sigmoid → Rating
Movie ID → Embedding → |
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License.

## 👨‍💻 Author

Built with ❤️ using cutting-edge technologies

## 🙏 Acknowledgments

- MovieLens for the dataset
- TMDB for the movie API
- The open-source community
