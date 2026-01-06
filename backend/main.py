import os
import requests
import json
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables (mostly for local dev)
load_dotenv()

app = FastAPI()

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for simplicity/development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Keys
TMDB_API_KEY = os.environ.get("TMDB_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

@app.get("/")
def read_root():
    return {"message": "VibeCheck API is running"}

@app.get("/analyze")
def analyze_movie(title: str = Query(..., description="The title of the movie to analyze")):
    if not TMDB_API_KEY or not GEMINI_API_KEY:
         raise HTTPException(status_code=500, detail="Missing API Keys in environment")

    # Step A: Search TMDB
    search_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={title}"
    try:
        search_res = requests.get(search_url).json()
        if not search_res.get("results"):
            raise HTTPException(status_code=404, detail="Movie not found on TMDB")
        
        movie = search_res["results"][0]
        movie_id = movie["id"]
        movie_title = movie["title"]
        poster_path = movie.get("poster_path")
        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TMDB Search Error: {str(e)}")

    # Step B: Fetch Reviews
    reviews_url = f"https://api.themoviedb.org/3/movie/{movie_id}/reviews?api_key={TMDB_API_KEY}"
    try:
        reviews_res = requests.get(reviews_url).json()
        results = reviews_res.get("results", [])
        # Get top 5 reviews
        reviews = [r["content"] for r in results[:5]]
        
        if not reviews:
             # Fallback if no reviews, use overview
             reviews = [movie.get("overview", "")]
             
    except Exception as e:
        print(f"Error fetching reviews: {e}")
        # Proceed with empty reviews or fallback
        reviews = [movie.get("overview", "")]

    # Step C: Analyze with Gemini
    reviews_text = "\n\n".join(reviews)
    prompt = (
        f"Analyze these reviews for the movie '{movie_title}'. "
        "Return a raw JSON object (no markdown formatting) with: "
        "'sentiment_summary' (1 sentence), 'vibe_tags' (list of 3-5 adjectives), "
        "and 'intensity_score' (1-10).\n\n"
        f"Reviews:\n{reviews_text}"
    )

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        text_response = response.text
        
        # Clean up potential markdown code blocks
        if text_response.startswith("```json"):
            text_response = text_response[7:-3]
        elif text_response.startswith("```"):
             text_response = text_response[3:-3]
             
        analysis = json.loads(text_response.strip())
        
        return {
            "movie_title": movie_title,
            "poster_url": poster_url,
            "analysis": analysis
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini Analysis Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
