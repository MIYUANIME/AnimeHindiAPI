#!/usr/bin/env python3
"""
Flask API to fetch video URLs from animedekho.co
This module provides a web API to get video URLs by scraping animedekho.co
"""

import re
import urllib.parse
from flask import Flask, jsonify, request
from playwright.sync_api import sync_playwright

app = Flask(__name__)

# Regular expression to match video URLs
VIDEO_RE = re.compile(r"https://play\.zephyrflick\.top/video/[A-Za-z0-9\-_]+", re.IGNORECASE)

def make_slugs(animetitle: str):
    """Create URL slugs from anime title"""
    base = animetitle.strip().lower()
    base = re.sub(r"[^\w\s-]", "", base)
    base = re.sub(r"\s+", "-", base)
    base = re.sub(r"-+", "-", base)
    # Remove leading and trailing hyphens
    base = base.strip("-")
    return [base, urllib.parse.quote_plus(base)]

def make_candidate_urls(slug, season, episode):
    """Generate candidate URLs to try"""
    return [
        f"https://animedekho.co/epi/{slug}-{season}x{episode}/",
        f"https://animedekho.co/episodes/{slug}-{season}x{episode}/",
        f"https://animedekho.co/epi/{slug}/{season}x{episode}/",
        f"https://animedekho.co/episodes/{slug}/{season}x{episode}/",
    ]

def fetch_video_url(animetitle: str, season: str, episode: str):
    """
    Fetch video URL from animedekho.co
    
    Args:
        animetitle (str): The anime title
        season (str): The season number
        episode (str): The episode number
        
    Returns:
        dict: Result dictionary with success status and video URL or error message
    """
    try:
        # Create slugs and candidate URLs
        slugs = make_slugs(animetitle)
        candidates = []
        for s in slugs:
            candidates.extend(make_candidate_urls(s, season, episode))
        
        # Launch browser and search for video URL
        with sync_playwright() as p:
            # Using Firefox as an alternative to Chromium which might be blocked by Cloudflare
            browser = p.firefox.launch(headless=True)
            context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0")
            page = context.new_page()
            found = None

            def on_request(request):
                nonlocal found
                url = request.url
                match = VIDEO_RE.search(url)
                if match:
                    found = match.group(0)
                    # Stop searching once we find a match
                    page.remove_listener("request", on_request)

            page.on("request", on_request)

            # Try each candidate URL
            for url in candidates:
                if found:
                    break
                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=20000)
                    # Wait briefly to let any JS/XHR fire
                    page.wait_for_timeout(3000)
                except Exception as e:
                    # Continue to next URL if this one fails
                    continue
            
            context.close()
            browser.close()
            
            if found:
                return {
                    "success": True,
                    "video_url": found,
                    "message": "Video URL found successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "No video URL found. Try different season/episode numbers.",
                    "message": "No video URL found"
                }
                
    except Exception as e:
        return {
            "success": False,
            "error": f"An error occurred: {str(e)}",
            "message": "Failed to fetch video URL"
        }

@app.route('/api/video', methods=['GET'])
def get_video_url():
    """
    API endpoint to fetch video URL
    
    Query Parameters:
        title (str): The anime title
        season (str): The season number
        episode (str): The episode number
        
    Returns:
        JSON: Result dictionary with success status and video URL or error message
    """
    # Get query parameters
    animetitle = request.args.get('title')
    season = request.args.get('season')
    episode = request.args.get('episode')
    
    # Validate input parameters
    if not animetitle or not season or not episode:
        return jsonify({
            "success": False,
            "error": "Missing required parameters: title, season, episode",
            "message": "Please provide title, season, and episode as query parameters"
        }), 400
    
    # Validate season and episode are numbers
    try:
        int(season)
        int(episode)
    except ValueError:
        return jsonify({
            "success": False,
            "error": "Invalid season or episode number",
            "message": "Season and episode must be valid numbers"
        }), 400
    
    # Fetch video URL
    result = fetch_video_url(animetitle, season, episode)
    
    # Return appropriate status code based on success
    if result["success"]:
        return jsonify(result), 200
    else:
        return jsonify(result), 404 if "No video URL found" in result.get("error", "") else 500

@app.route('/', methods=['GET'])
def home():
    """Home endpoint with API documentation"""
    return jsonify({
        "message": "AnimeDekho API",
        "description": "API to fetch video URLs from animedekho.co",
        "endpoints": {
            "/api/video": {
                "method": "GET",
                "description": "Fetch video URL for an anime episode",
                "parameters": {
                    "title": "Anime title (string)",
                    "season": "Season number (integer)",
                    "episode": "Episode number (integer)"
                },
                "example": "/api/video?title=shinchan&season=1&episode=1"
            }
        }
    }), 200

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "AnimeDekho API is running"
    }), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)