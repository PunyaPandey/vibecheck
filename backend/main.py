import os
import requests
import json
import re
import logging
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from bytez import Bytez
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
BYTEZ_API_KEY = os.environ.get("BYTEZ_API_KEY")

if not BYTEZ_API_KEY:
    logger.warning("BYTEZ_API_KEY is not set.")

if not TMDB_API_KEY:
    logger.warning("TMDB_API_KEY is not set.")

@app.get("/")
def read_root():
    return {"message": "VibeCheck API is running"}

@app.get("/analyze")
def analyze_movie(title: str = Query(..., description="The title of the movie to analyze")):
    logger.info(f"Received analysis request for title: {title}")
    
    if not TMDB_API_KEY or not BYTEZ_API_KEY:
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

    # Step C: Analyze with Bytez
    reviews_text = "\n\n".join(reviews)
    # Truncate reviews safely
    if len(reviews_text) > 5000:
        reviews_text = reviews_text[:5000]
        
    prompt = (
        f"Analyze these reviews for the movie '{movie_title}'. "
        "Return a strictly valid JSON object (no markdown formatting, no comments) with keys: "
        "'sentiment_summary' (1 sentence string), 'vibe_tags' (list of 3-5 strings), "
        "and 'intensity_score' (integer 1-10).\n\n"
        f"Reviews:\n{reviews_text}"
    )

    try:
        logger.info("Initializing Bytez client...")
        sdk = Bytez(BYTEZ_API_KEY)
        model = sdk.model("google/gemini-2.5-flash")
        
        logger.info("Sending request to Bytez...")
        results = model.run([
            {
                "role": "user",
                "content": prompt
            }
        ])
        
        if results.error:
             logger.error(f"Bytez API Error: {results.error}")
             raise Exception(f"Bytez API Error: {results.error}")

        text_response = results.output
        logger.info(f"Bytez Raw Response: {text_response}")

        # specific cleaning for JSON
        match = re.search(r'\{.*\}', text_response, re.DOTALL)
        if match:
            json_str = match.group(0)
            analysis = json.loads(json_str)
        else:
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
        logger.error(f"AI Analysis Error: {e}")
        raise HTTPException(status_code=500, detail=f"AI Analysis Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
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

    # List of models to try in order of preference
    # 'gemini-2.0-flash' is new and fast but might be rate limited
    # 'gemini-1.5-flash' is the standard stable version
    models_to_try = ['gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-1.5-flash-001', 'gemini-pro']
    
    analysis = None
    last_error = None

    import time

    for model_name in models_to_try:
        if analysis:
            break
            
        logger.info(f"Attempting analysis with model: {model_name}")
        
        # Simple retry logic for 429s (Rate Limit)
        max_retries = 3
        for attempt in range(max_retries):
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                text_response = response.text
                
                logger.info(f"Gemini Raw Response ({model_name}): {text_response}")

                # specific cleaning for JSON
                match = re.search(r'\{.*\}', text_response, re.DOTALL)
                if match:
                    json_str = match.group(0)
                    analysis = json.loads(json_str)
                else:
                    analysis = json.loads(text_response)
                
                # If we got here, success! Break the retry loop
                break

            except Exception as e:
                # Check directly if it's a 429/quota error first
                error_str = str(e)
                if "429" in error_str or "quota" in error_str.lower():
                    logger.warning(f"Rate limit hit for {model_name} (Attempt {attempt+1}/{max_retries}). Retrying in 4s...")
                    time.sleep(4) # Wait 4 seconds as suggested by error
                    last_error = e
                    continue # Retry same model
                elif "404" in error_str:
                     logger.warning(f"Model {model_name} not found. Skipping to next model.")
                     last_error = e
                     break # Stop retrying this model, move to next model
                else:
                    logger.error(f"Error with {model_name}: {e}")
                    last_error = e
                    break # Unknown error, try next model
    
    if not analysis:
        error_detail = f"All models failed. Last error: {str(last_error)}"
        if "429" in str(last_error):
             raise HTTPException(status_code=429, detail="Server is busy (Rate Limit). Please try again in a few seconds.")
        raise HTTPException(status_code=500, detail=error_detail)

    return {
        "movie_title": movie_title,
        "poster_url": poster_url,
        "analysis": analysis
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
