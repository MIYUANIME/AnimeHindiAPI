#!/usr/bin/env python3
"""
Module to fetch video URLs from animedekho.co
This module provides functions to get video URLs by scraping animedekho.co
"""

import re
import urllib.parse
from playwright.sync_api import sync_playwright

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
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
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

# For testing purposes when running directly
if __name__ == "__main__":
    import sys
    import json
    if len(sys.argv) == 4:
        # Command line usage: python video.py "anime title" season episode
        animetitle = sys.argv[1]
        season = sys.argv[2]
        episode = sys.argv[3]
        result = fetch_video_url(animetitle, season, episode)
        print(json.dumps(result))
    else:
        print("Usage: python video.py 'anime title' season episode")
        print("Example: python video.py 'shinchan' 1 1")
