import requests
import time

def test_gateway():
    print("Testing API Gateway /generate-song endpoint...")
    url = "http://localhost:8000/generate-song"
    payload = {
        "prompt": "a chill lofi beat",
        "style": "Lo-Fi"
    }

    try:
        response = requests.post(url, json=payload, timeout=300)
        print("Status code:", response.status_code)
        print("Response:", response.json())
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test_gateway()
