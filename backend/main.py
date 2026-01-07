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

    # Step C: Analyze with Bytez (Llama 3 + Flux)
    reviews_text = "\n\n".join(reviews)
    if len(reviews_text) > 4000:
        reviews_text = reviews_text[:4000]
        
    prompt = (
        f"Analyze these reviews for the movie '{movie_title}'. "
        "Return a strictly valid JSON object (no markdown formatting, no comments) with keys: "
        "'sentiment_summary' (1 sentence string), 'vibe_tags' (list of 3-5 strings), "
        "'intensity_score' (integer 1-10), "
        "'visual_prompt' (string: a detailed, artistic description of a poster that captures the movie's vibe, suitable for an image generator).\n\n"
        f"Reviews:\n{reviews_text}"
    )

    try:
        logger.info("Initializing Bytez client...")
        sdk = Bytez(BYTEZ_API_KEY)
        
        # 1. Text Analysis with Phi-3 Mini (Free Tier Compatible)
        logger.info("Running text analysis with Phi-3 Mini...")
        text_model = sdk.model("microsoft/Phi-3-mini-4k-instruct")
        text_results = text_model.run([
            {
                "role": "user",
                "content": prompt
            }
        ])
        
        if text_results.error:
             # Try fallback to raw string if error is just a structure issue, but usually error is API level
             logger.error(f"Bytez Llama Error: {text_results.error}")
             raise Exception(f"Bytez Llama Error: {text_results.error}")

        text_response = text_results.output
        logger.info(f"Llama Response: {text_response}")

        # Parse JSON
        analysis = {}
        if isinstance(text_response, dict):
            analysis = text_response
        else:
            match = re.search(r'\{.*\}', text_response, re.DOTALL)
            if match:
                json_str = match.group(0)
                try:
                    analysis = json.loads(json_str)
                except:
                    pass
            
            if not analysis:
                 try:
                    analysis = json.loads(text_response)
                 except:
                    # Fallback if JSON fails
                    analysis = {
                        "sentiment_summary": "Vibes are mysterious...",
                        "vibe_tags": ["Mystery", "Unknown"],
                        "intensity_score": 5,
                        "visual_prompt": f"A mysterious abstract poster for the movie {movie_title}"
                    }

        # 2. Image Generation with Flux
        visual_prompt = analysis.get("visual_prompt", f"A creative poster for {movie_title}")
        logger.info(f"Generating image with Flux. Prompt: {visual_prompt}")
        
        image_model = sdk.model("fal/FLUX.2-dev-Turbo")
        image_results = image_model.run(visual_prompt)
        
        generated_image_url = None
        if image_results.error:
            logger.error(f"Flux Error: {image_results.error}")
        else:
            # Flux output is typically a URL string or a dict with url
            img_out = image_results.output
            if isinstance(img_out, dict):
                generated_image_url = img_out.get("images", [{}])[0].get("url") or img_out.get("url")
            elif isinstance(img_out, str):
                generated_image_url = img_out # Assuming direct URL string
            elif isinstance(img_out, list) and len(img_out) > 0:
                 generated_image_url = img_out[0].get("url") if isinstance(img_out[0], dict) else img_out[0]

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
