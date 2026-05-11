import requests
import json
import time

GATEWAY_URL = "http://127.0.0.1:8000"

def test_song_generation():
    print("--- Testing AI Music Studio Pipeline (with RVC) ---")
    
    # 1. Check health
    try:
        resp = requests.get(f"{GATEWAY_URL}/health")
        print(f"Gateway Health: {resp.json()}")
    except Exception as e:
        print(f"Error connecting to gateway: {e}")
        return

    # 2. Get voice profiles (need one for RVC)
    print("Fetching voice profiles...")
    profiles_resp = requests.get(f"{GATEWAY_URL}/voice-profiles")
    profiles = profiles_resp.json().get("profiles", [])
    
    if not profiles:
        print("No voice profiles found. Please create one first or the test will use default (RVC might skip).")
        profile_id = None
    else:
        profile_id = profiles[0].get("id")
        print(f"Using profile: {profile_id}")

    # 3. Generate Song
    payload = {
        "prompt": "Baharın gelişi ve doğanın uyanışı hakkında neşeli bir şarkı",
        "style": "Pop, upbeat, acoustic guitar",
        "language": "tr",
        "features": ["lyrics", "music", "voice"],
        "enhance_prompt": True,
        "voice_profile_id": profile_id,
        "use_rvc": True,
        "rvc_pitch": 0,
        "rvc_index_rate": 0.75
    }

    print(f"Sending request to /generate-song...")
    start_time = time.time()
    
    try:
        # Long timeout because RVC + MusicGen takes time
        resp = requests.post(f"{GATEWAY_URL}/generate-song", json=payload, timeout=600)
        result = resp.json()
        
        duration = time.time() - start_time
        print(f"Request completed in {duration:.2f} seconds.")
        
        if result.get("status") == "success":
            print("\n--- Generation Success! ---")
            print(f"Title: {result.get('song_title')}")
            print(f"Lyrics snippet: {result.get('lyrics')[:100]}...")
            print(f"Final MP3: {result.get('final_song')}")
            print(f"Enhanced Prompt: {result.get('enhanced_prompt')}")
            print(f"Output URL: {GATEWAY_URL}/outputs/{result.get('final_song')}")
        else:
            print(f"\n--- Generation Failed ---")
            print(f"Error: {result.get('message')}")
            
    except Exception as e:
        print(f"Error during request: {e}")

if __name__ == "__main__":
    test_song_generation()
