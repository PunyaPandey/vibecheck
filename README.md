# VibeCheck

VibeCheck is a movie recommendation application that uses Google Gemini AI to analyze movie vibes based on sentiment, rather than just genre.

## Project Structure (Monorepo)

```
/
├── backend/            # FastAPI Backend
│   ├── main.py
│   └── requirements.txt
├── frontend/           # React + Vite Frontend
│   ├── src/
│   ├── package.json
│   ├── vite.config.js
│   └── ...
└── README.md
```

## 🚀 Deployment on Render

This project is set up to be deployed as a Monorepo on Render. You will create two separate services (Web Service for Backend, Static Site for Frontend) connected to the same repository.

### 1. Backend Service (Web Service)

1.  **Create a New Web Service** on Render.
2.  **Connect** your GitHub repository.
3.  **Settings:**
    *   **Name:** `vibecheck-backend` (or similar)
    *   **Root Directory:** `backend`
    *   **Runtime:** `Python 3`
    *   **Build Command:** `pip install -r requirements.txt`
    *   **Start Command:** `uvicorn main:app --host 0.0.0.0 --port 10000`
    *   **Environment Variables:**
        *   `TMDB_API_KEY`: Your TMDB API Key
        *   `GEMINI_API_KEY`: Your Google Gemini API Key

### 2. Frontend Service (Static Site)

1.  **Create a New Static Site** on Render.
2.  **Connect** the same GitHub repository.
3.  **Settings:**
    *   **Name:** `vibecheck-frontend`
    *   **Root Directory:** `frontend`
    *   **Build Command:** `npm install && npm run build`
    *   **Publish Directory:** `dist`
    *   **Environment Variables:**
        *   `VITE_API_URL`: The URL of your deployed Backend Service (e.g., `https://vibecheck-backend.onrender.com`) - *Do not include a trailing slash.*

## 🛠 Local Development

### Prerequisites
*   Python 3.8+
*   Node.js & npm

### Backend Setup
1.  Navigate to the backend: `cd backend`
2.  Create a virtual environment: `python -m venv venv`
3.  Activate it: `source venv/bin/activate` (Mac/Linux) or `venv\Scripts\activate` (Windows)
4.  Install dependencies: `pip install -r requirements.txt`
5.  Create a `.env` file in `backend/` with your keys:
    ```
    TMDB_API_KEY=your_key
    GEMINI_API_KEY=your_key
    ```
6.  Run the server: `uvicorn main:app --reload`
    *   Server runs at `http://localhost:8000`

### Frontend Setup
1.  Open a new terminal.
2.  Navigate to the frontend: `cd frontend`
3.  Install dependencies: `npm install`
4.  Run the dev server: `npm run dev`
    *   App runs at `http://localhost:5173`
