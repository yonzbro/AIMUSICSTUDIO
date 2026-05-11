"""
Antigravity AI Music Studio - Service Health & Function Test
Tests each service individually to verify they work correctly.
"""
import requests
import time
import sys

GATEWAY = "http://127.0.0.1:8000"
SERVICES = {
    "lyrics":  "http://127.0.0.1:8001",
    "music":   "http://127.0.0.1:8002",
    "voice":   "http://127.0.0.1:8003",
    "clone":   "http://127.0.0.1:8004",
    "remix":   "http://127.0.0.1:8005",
    "rvc":     "http://127.0.0.1:8006",
}

def test_health(name, url):
    """Test if a service is alive."""
    try:
        r = requests.get(f"{url}/health", timeout=5)
        ok = r.status_code == 200
        print(f"  {'✅' if ok else '❌'} {name:12s} health: {r.status_code}")
        return ok
    except Exception as e:
        print(f"  ❌ {name:12s} health: {e}")
        return False

def test_lyrics():
    """Test lyrics generation (Qwen2-1.5B)."""
    print("\n🎵 Testing LYRICS (Qwen2-1.5B)...")
    try:
        r = requests.post(
            f"{SERVICES['lyrics']}/generate-lyrics",
            json={"prompt": "A short test song about AI"},
            timeout=120
        )
        data = r.json()
        lyrics = data.get("lyrics", "")
        if lyrics and len(lyrics) > 10:
            print(f"  ✅ Lyrics generated ({len(lyrics)} chars)")
            print(f"     Preview: {lyrics[:100]}...")
            return True
        else:
            print(f"  ❌ Lyrics empty or too short: {data}")
            return False
    except Exception as e:
        print(f"  ❌ Lyrics failed: {e}")
        return False

def test_music():
    """Test music generation (MusicGen-small)."""
    print("\n🎸 Testing MUSIC (MusicGen-small)...")
    try:
        r = requests.post(
            f"{SERVICES['music']}/generate-music",
            json={"prompt": "upbeat electronic melody", "duration": 5},
            timeout=120
        )
        data = r.json()
        audio_url = data.get("audio_url", "")
        if audio_url:
            print(f"  ✅ Music generated: {audio_url}")
            return True
        else:
            print(f"  ❌ Music empty: {data}")
            return False
    except Exception as e:
        print(f"  ❌ Music failed: {e}")
        return False

def test_voice():
    """Test voice synthesis (XTTS-v2)."""
    print("\n🎙️ Testing VOICE (XTTS-v2)...")
    try:
        r = requests.post(
            f"{SERVICES['voice']}/generate-voice",
            json={"text": "Hello world, this is a test.", "language": "en"},
            timeout=180
        )
        data = r.json()
        voice_file = data.get("voice_file", "")
        if voice_file:
            print(f"  ✅ Voice generated: {voice_file}")
            return True
        else:
            print(f"  ❌ Voice empty: {data}")
            return False
    except Exception as e:
        print(f"  ❌ Voice failed: {e}")
        return False

def test_clone():
    """Test clone service health (no file upload needed)."""
    print("\n🧬 Testing CLONE (Voice Profile Manager)...")
    try:
        r = requests.get(f"{SERVICES['clone']}/profiles", timeout=10)
        data = r.json()
        print(f"  ✅ Clone service OK - {data.get('total', 0)} profiles found")
        return True
    except Exception as e:
        print(f"  ❌ Clone failed: {e}")
        return False

def test_rvc():
    """Test RVC service health."""
    print("\n✨ Testing RVC (Voice Conversion)...")
    try:
        r = requests.get(f"{SERVICES['rvc']}/health", timeout=10)
        if r.status_code == 200:
            print(f"  ✅ RVC service alive")
            # Check model status
            r2 = requests.get(f"{SERVICES['rvc']}/model-status", timeout=10)
            if r2.status_code == 200:
                data = r2.json()
                loaded = data.get("loaded", False)
                print(f"     Model loaded: {loaded}")
            return True
        return False
    except Exception as e:
        print(f"  ❌ RVC failed: {e}")
        return False

def main():
    print("=" * 55)
    print("  ANTIGRAVITY AI MUSIC STUDIO - SERVICE TEST")
    print("=" * 55)
    
    # Phase 1: Health checks
    print("\n📡 Phase 1: Health Checks")
    print("-" * 40)
    all_alive = True
    for name, url in SERVICES.items():
        if not test_health(name, url):
            all_alive = False
    test_health("gateway", GATEWAY)
    
    if not all_alive:
        print("\n⚠️  Some services are down. Fix them before testing.")
    
    # Phase 2: Functional tests (sequential to avoid GPU conflicts)
    print("\n\n🧪 Phase 2: Functional Tests (Sequential)")
    print("-" * 40)
    
    results = {}
    
    # Test 1: Lyrics
    results["lyrics"] = test_lyrics()
    time.sleep(2)
    
    # Test 2: Music  
    results["music"] = test_music()
    time.sleep(2)
    
    # Test 3: Voice
    results["voice"] = test_voice()
    time.sleep(2)
    
    # Test 4: Clone
    results["clone"] = test_clone()
    
    # Test 5: RVC
    results["rvc"] = test_rvc()
    
    # Summary
    print("\n\n" + "=" * 55)
    print("  RESULTS SUMMARY")
    print("=" * 55)
    for name, ok in results.items():
        print(f"  {'✅' if ok else '❌'} {name}")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"\n  Score: {passed}/{total} services working")
    
    if passed == total:
        print("  🎉 ALL SYSTEMS GO! Ready to create music!")
    else:
        print("  ⚠️  Some services need attention.")
    
    print("=" * 55)

if __name__ == "__main__":
    main()
