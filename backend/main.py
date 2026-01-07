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
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    logger.warning("GOOGLE_API_KEY is not set.")

if not TMDB_API_KEY:
    logger.warning("TMDB_API_KEY is not set.")

@app.get("/")
def read_root():
    return {"message": "VibeCheck API is running"}

@app.get("/analyze")
def analyze_movie(title: str = Query(..., description="The title of the movie to analyze")):
    logger.info(f"Received analysis request for title: {title}")
    
    if not TMDB_API_KEY or not GOOGLE_API_KEY:
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

    # Step C: Analyze with Gemini 1.5 Flash + Pollinations.ai
    reviews_text = "\n\n".join(reviews)
    if len(reviews_text) > 4000:
        reviews_text = reviews_text[:4000]
        
    prompt = (
        f"You are a movie vibe analyst. Analyze these reviews for the movie '{movie_title}'. "
        "Return a strictly valid JSON object (no markdown formatting, no comments) with the following keys:\n"
        "- 'sentiment_summary': A 1-sentence summary of the general sentiment.\n"
        "- 'vibe_tags': A list of 3-5 short string tags capturing the mood.\n"
        "- 'intensity_score': An integer from 1 to 10.\n"
        "- 'visual_prompt': A detailed, artistic description of a poster that captures the movie's vibe, suitable for an image generator.\n\n"
        f"Reviews:\n{reviews_text}"
    )

    try:
        logger.info("Initializing Gemini client...")
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"response_mime_type": "application/json"})
        
        # 1. Text Analysis with Gemini 1.5 Flash
        logger.info("Running text analysis with Gemini 1.5 Flash...")
        text_response = None
        
        # List of models to try in order
        models_to_try = ['gemini-1.5-flash', 'gemini-1.5-flash-001', 'gemini-1.5-flash-latest', 'gemini-pro']
        
        for model_name in models_to_try:
            try:
                logger.info(f"Attempting to use model: {model_name}")
                model = genai.GenerativeModel(model_name, generation_config={"response_mime_type": "application/json"})
                response = model.generate_content(prompt)
                text_response = response.text
                logger.info(f"Gemini Response from {model_name}: {text_response}")
                break # Success
            except Exception as e:
                logger.warning(f"Failed with model {model_name}: {e}")
                if "404" in str(e) or "not found" in str(e).lower():
                    # Only list models once if real 404
                    if model_name == models_to_try[0]:
                        try:
                            logger.info("Listing available models to debug 404:")
                            for m in genai.list_models():
                                logger.info(f" - {m.name}")
                        except Exception as list_err:
                            logger.error(f"Could not list models: {list_err}")
                continue # Try next model
        
        if not text_response:
             raise Exception("All Gemini models failed.")

        # Parse JSON
        try:
            analysis = json.loads(text_response)
        except json.JSONDecodeError:
             logger.error("Failed to parse Gemini JSON response")
             # Fallback
             analysis = {
                "sentiment_summary": "Vibes are mysterious...",
                "vibe_tags": ["Mystery", "Unknown"],
                "intensity_score": 5,
                "visual_prompt": f"A mysterious abstract poster for the movie {movie_title}"
            }

        # 2. Image Generation with Pollinations.ai (Free)
        visual_prompt = analysis.get("visual_prompt", f"A creative poster for {movie_title}")
        logger.info(f"Generating image with Pollinations.ai. Prompt: {visual_prompt}")
        
        # Pollinations is URL based, no API key needed
        # We need to URL encode the prompt
        encoded_prompt = requests.utils.quote(visual_prompt)
        generated_image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&model=flux&nologo=true"
        
        logger.info(f"Generated Image URL: {generated_image_url}")
        
        return {
            "movie_title": movie_title,
            "poster_url": poster_url,
            "analysis": analysis,
            "generated_image_url": generated_image_url
        }

    except Exception as e:
        logger.error(f"AI Analysis Error: {e}")
        # Return partial results if AI fails? No, app expects structure.
        # But we can return a fallback structure to avoid frontend crash
        raise HTTPException(status_code=500, detail=f"AI Analysis Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
