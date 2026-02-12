#!/usr/bin/env python3
"""
Demonstration of HardCard Content Generation Capabilities
=========================================================
This script showcases all the content generation engines found in the HardCard system:
1. Sacred Geometry Poetry (sonnets, haikus, villanelles)
2. Music Video Generation Pipeline
3. Muse Creative Discovery System
4. Music Generation via Suno API
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"  # Adjust if backend is running on different port
AUTH_TOKEN = "demo-token"  # Replace with actual auth token if needed

def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'='*80}")
    print(f"{title.center(80)}")
    print(f"{'='*80}\n")

def make_api_request(endpoint: str, method: str = "POST", data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Make an API request to the backend"""
    url = f"{BASE_URL}{endpoint}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AUTH_TOKEN}"
    }
    
    try:
        if method == "POST":
            response = requests.post(url, json=data, headers=headers)
        else:
            response = requests.get(url, headers=headers)
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
        return {"error": str(e)}

# 1. SACRED GEOMETRY POETRY GENERATION
def demo_sacred_geometry_poetry():
    print_section("SACRED GEOMETRY POETRY GENERATION")
    
    # Generate a Sonnet with Golden Ratio (Phi)
    print("1. Generating a Sonnet using Golden Ratio (Phi)...")
    sonnet_request = {
        "form_type": "sonnet",
        "sacred_constant": "phi",
        "theme": "cosmos",
        "entropy_source": "hardware",
        "constraint_level": 0.8,
        "recursion_depth": 3
    }
    
    sonnet_result = make_api_request("/sacred-geometry-poetry/generate", data=sonnet_request)
    if "poem" in sonnet_result:
        print(f"\nSONNET (Golden Ratio Constrained):")
        print("-" * 40)
        print(sonnet_result["poem"])
        print(f"\nMathematical Score: {sonnet_result['blueprint']['mathematical_score']:.3f}")
        print(f"Sacred Basis: {sonnet_result['blueprint']['sacred_geometry_basis']['properties']}")
    
    time.sleep(2)
    
    # Generate a Haiku with Fibonacci
    print("\n2. Generating a Haiku using Fibonacci Sequence...")
    haiku_request = {
        "form_type": "haiku",
        "sacred_constant": "fibonacci",
        "theme": "nature",
        "entropy_source": "time",
        "constraint_level": 0.9,
        "recursion_depth": 2
    }
    
    haiku_result = make_api_request("/sacred-geometry-poetry/generate", data=haiku_request)
    if "poem" in haiku_result:
        print(f"\nHAIKU (Fibonacci Constrained):")
        print("-" * 40)
        print(haiku_result["poem"])
        print(f"\nMathematical Score: {haiku_result['blueprint']['mathematical_score']:.3f}")
    
    time.sleep(2)
    
    # Generate a Villanelle with Pi
    print("\n3. Generating a Villanelle using Pi...")
    villanelle_request = {
        "form_type": "villanelle",
        "sacred_constant": "pi",
        "theme": "time",
        "entropy_source": "pseudo",
        "constraint_level": 0.7,
        "recursion_depth": 4
    }
    
    villanelle_result = make_api_request("/sacred-geometry-poetry/generate", data=villanelle_request)
    if "poem" in villanelle_result:
        print(f"\nVILLANELLE (Pi Constrained):")
        print("-" * 40)
        print(villanelle_result["poem"])
        print(f"\nMathematical Score: {villanelle_result['blueprint']['mathematical_score']:.3f}")

# 2. MUSIC VIDEO GENERATION
def demo_music_video_generation():
    print_section("MUSIC VIDEO GENERATION PIPELINE")
    
    print("Initiating music video generation from text prompt...")
    video_request = {
        "prompt": "A journey through cosmic consciousness, exploring the mathematical beauty of the universe",
        "title": "Cosmic Mathematics Symphony",
        "duration": 30,
        "style": "abstract-scientific",
        "optimize_for_m4": True,
        "mode": "autonomous"
    }
    
    # Start generation
    video_result = make_api_request("/music-video/generate", data=video_request)
    if "video_id" in video_result:
        video_id = video_result["video_id"]
        print(f"\nVideo ID: {video_id}")
        print(f"Title: {video_result['title']}")
        print(f"Status: {video_result['status']}")
        
        # Show pipeline steps
        print("\nPipeline Steps:")
        for step in video_result["steps"]:
            print(f"  - {step['name']}: {step['status']}")
        
        # Poll for status updates
        print("\nTracking generation progress...")
        for i in range(5):
            time.sleep(3)
            status = make_api_request(f"/music-video/status/{video_id}", method="GET")
            if "steps" in status:
                print(f"\nUpdate {i+1}:")
                for step in status["steps"]:
                    print(f"  - {step['name']}: {step['status']}")
                
                if status["status"] == "completed":
                    print(f"\n✓ Video completed!")
                    print(f"Video URL: {status.get('video_url', 'Processing...')}")
                    print(f"Thumbnail: {status.get('thumbnail_url', 'Processing...')}")
                    break

# 3. MUSE CREATIVE DISCOVERY
def demo_muse_discovery():
    print_section("MUSE CREATIVE DISCOVERY SYSTEM")
    
    # First, assess user's muse archetype
    print("1. Assessing your creative frequency signature...")
    assessment_request = {
        "user_preferences": {
            "creative_domains": ["cosmos", "mathematics", "poetry", "music"],
            "personality_traits": {
                "analysis": 0.8,
                "creativity": 0.9,
                "spirituality": 0.7,
                "humor": 0.6
            },
            "mathematical_preference": "golden_ratio_and_pi"
        },
        "creative_history": ["poetry", "music", "visual_arts"],
        "entropy_source": "hardware",
        "depth_level": 3
    }
    
    signature = make_api_request("/muse/assess", data=assessment_request)
    if "primary_muse" in signature:
        print(f"\nYour Creative DNA: {signature['creative_dna']}")
        print(f"Primary Muse: {signature['primary_muse'].upper()}")
        print(f"Secondary Muse: {signature['secondary_muse'].upper()}")
        print(f"Frequency: {signature['mathematical_coordinates']['frequency_hz']:.1f} Hz")
        
        # Now discover creative expression
        print("\n2. Discovering creative expression based on your frequency...")
        discovery_request = {
            "frequency_signature": signature,
            "discovery_theme": "universal consciousness",
            "form_preference": "auto",
            "real_time_streaming": False
        }
        
        discovery = make_api_request("/muse/discover", data=discovery_request)
        if "discovered_expression" in discovery:
            print(f"\nDISCOVERED EXPRESSION:")
            print("-" * 40)
            print(discovery["discovered_expression"])
            print(f"\nMuse Resonance Score: {discovery['muse_resonance_score']:.3f}")
            print(f"Creative Coordinates:")
            coords = discovery["creative_coordinates"]
            print(f"  - Phi Position: {coords['phi_position']:.3f}")
            print(f"  - Pi Resonance: {coords['pi_resonance']:.3f}")
            print(f"  - Fibonacci Sequence: {coords['fibonacci_sequence']}")
            print(f"  - Euler Growth: {coords['euler_growth']:.3f}")

# 4. MUSIC GENERATION
def demo_music_generation():
    print_section("SUNO MUSIC GENERATION")
    
    print("Generating music for a mathematical concept...")
    music_request = {
        "concept_id": "sacred-geometry-001",
        "concept_name": "Sacred Geometry Symphony",
        "concept_description": "A musical exploration of the golden ratio and fibonacci sequences in nature",
        "mood": "mystical",
        "genre": "ambient",
        "duration": 45
    }
    
    music_result = make_api_request("/suno-music/generate-music", data=music_request)
    if "music_id" in music_result:
        print(f"\nMusic ID: {music_result['music_id']}")
        print(f"Title: {music_result['title']}")
        print(f"Status: {music_result['status']}")
        print(f"Audio URL: {music_result.get('audio_url', 'Processing...')}")
        print(f"Detected Mood: {music_result.get('mood', 'N/A')}")
        print(f"Detected Genre: {music_result.get('genre', 'N/A')}")

# 5. SHOWCASE ALL MUSE ARCHETYPES
def showcase_muse_archetypes():
    print_section("NINE MUSE ARCHETYPES")
    
    archetypes = make_api_request("/muse/archetypes", method="GET")
    if "archetypes" in archetypes:
        for name, data in archetypes["archetypes"].items():
            print(f"\n{data['name']}:")
            print(f"  - Frequency: {data['frequency_hz']} Hz")
            print(f"  - Sacred Constant: {data['sacred_constant']}")
            print(f"  - Creative Domains: {', '.join(data['creative_domains'])}")
            print(f"  - Archetypal Strengths: {', '.join(data['archetypal_strengths'])}")

def main():
    print_section("HARDCARD CONTENT GENERATION SHOWCASE")
    print("Demonstrating all content generation capabilities...")
    print("Make sure the backend is running on http://localhost:8000")
    
    # Run all demos
    try:
        # 1. Sacred Geometry Poetry
        demo_sacred_geometry_poetry()
        time.sleep(2)
        
        # 2. Music Video Generation
        demo_music_video_generation()
        time.sleep(2)
        
        # 3. Muse Discovery
        demo_muse_discovery()
        time.sleep(2)
        
        # 4. Music Generation
        demo_music_generation()
        time.sleep(2)
        
        # 5. Show all Muses
        showcase_muse_archetypes()
        
        print_section("DEMONSTRATION COMPLETE")
        print("All content generation systems have been showcased!")
        print("\nNote: Some features may return mock data if external APIs are not configured.")
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n\nError during demo: {e}")

if __name__ == "__main__":
    main()