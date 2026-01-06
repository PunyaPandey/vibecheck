import os
import requests
import json
import re
import logging
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
else:
    logger.warning("GEMINI_API_KEY is not set.")

if not TMDB_API_KEY:
    logger.warning("TMDB_API_KEY is not set.")

@app.get("/list_models")
def list_models():
    if not GEMINI_API_KEY:
         raise HTTPException(status_code=500, detail="GEMINI_API_KEY is not set.")
    try:
        models = [m.name for m in genai.list_models()]
        return {"models": models}
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Error listing models: {str(e)}")

@app.get("/")
def read_root():
    return {"message": "VibeCheck API is running"}

@app.get("/analyze")
def analyze_movie(title: str = Query(..., description="The title of the movie to analyze")):
    logger.info(f"Received analysis request for title: {title}")
    
    if not TMDB_API_KEY or not GEMINI_API_KEY:
         logger.error("Missing API Keys")
         raise HTTPException(status_code=500, detail="Missing API Keys in environment")

    # Step A: Search TMDB
    search_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={title}"
    try:
        response = requests.get(search_url)
        response.raise_for_status() # Raise error for non-2xx codes
        search_res = response.json()
        
        if not search_res.get("results"):
            logger.info(f"Movie found not found for query: {title}")
            raise HTTPException(status_code=404, detail="Movie not found on TMDB")
        
        movie = search_res["results"][0]
        movie_id = movie["id"]
        movie_title = movie["title"]
        poster_path = movie.get("poster_path")
        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
        
        logger.info(f"Found movie: {movie_title} (ID: {movie_id})")
        
    except requests.exceptions.HTTPError as e:
        logger.error(f"TMDB HTTP Error: {e}")
        raise HTTPException(status_code=502, detail=f"TMDB API Error: {str(e)}")
    except Exception as e:
        logger.error(f"TMDB Search Unexpected Error: {e}")
        raise HTTPException(status_code=500, detail=f"TMDB Search Error: {str(e)}")

    # Step B: Fetch Reviews
    reviews_url = f"https://api.themoviedb.org/3/movie/{movie_id}/reviews?api_key={TMDB_API_KEY}"
    try:
        reviews_res = requests.get(reviews_url).json()
        results = reviews_res.get("results", [])
        # Get top 5 reviews
        reviews = [r["content"] for r in results[:5]]
        
        if not reviews:
             logger.info("No reviews found, falling back to overview.")
             reviews = [movie.get("overview", "")]
             
    except Exception as e:
        logger.error(f"Error fetching reviews: {e}")
        # Proceed with empty reviews or fallback
        reviews = [movie.get("overview", "")]

    # Step C: Analyze with Gemini
    reviews_text = "\n\n".join(reviews)
    # Truncate reviews to avoid context limit (simple safeguard)
    if len(reviews_text) > 10000:
        reviews_text = reviews_text[:10000]
        
    prompt = (
        f"Analyze these reviews for the movie '{movie_title}'. "
        "Return a strictly valid JSON object (no markdown formatting, no comments) with keys: "
        "'sentiment_summary' (1 sentence string), 'vibe_tags' (list of 3-5 strings), "
        "and 'intensity_score' (integer 1-10).\n\n"
        f"Reviews:\n{reviews_text}"
    )

    try:
        # Use specific version to avoid alias issues
        # Try gemini-1.5-flash-001 or gemini-pro if flash fails
        model_name = 'gemini-1.5-flash-001' 
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        text_response = response.text
        
        logger.info(f"Gemini Raw Response: {text_response}")

        # specific cleaning for JSON
        # Find the first '{' and the last '}'
        match = re.search(r'\{.*\}', text_response, re.DOTALL)
        if match:
            json_str = match.group(0)
            analysis = json.loads(json_str)
        else:
             # Fallback: try straight load
             analysis = json.loads(text_response)
        
        return {
            "movie_title": movie_title,
            "poster_url": poster_url,
            "analysis": analysis
        }

    except json.JSONDecodeError as e:
        logger.error(f"JSON Parse Error. Response was: {text_response}. Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to parse AI response")
    except Exception as e:
        logger.error(f"Gemini Analysis Error: {e}")
        raise HTTPException(status_code=500, detail=f"Gemini Analysis Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
