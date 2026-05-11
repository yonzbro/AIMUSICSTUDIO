import os
import urllib.request
from tqdm import tqdm

MODELS_DIR = "/app/models/pretrained"

# Standard RVC v2 required models
REQUIRED_MODELS = {
    "hubert_base.pt": "https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/hubert_base.pt",
    "rmvpe.pt": "https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/rmvpe.pt"
}

def download_file(url, destination):
    if os.path.exists(destination):
        return
    
    print(f"Downloading {url} to {destination}...")
    
    class DownloadProgressBar(tqdm):
        def update_to(self, b=1, bsize=1, tsize=None):
            if tsize is not None:
                self.total = tsize
            self.update(b * bsize - self.n)

    with DownloadProgressBar(unit='B', unit_scale=True, miniters=1, desc=url.split('/')[-1]) as t:
        urllib.request.urlretrieve(url, filename=destination, reporthook=t.update_to)

def check_and_download_models():
    os.makedirs(MODELS_DIR, exist_ok=True)
    for filename, url in REQUIRED_MODELS.items():
        dest = os.path.join(MODELS_DIR, filename)
        if not os.path.exists(dest):
            download_file(url, dest)
        else:
            print(f"Model {filename} already exists.")

if __name__ == "__main__":
    check_and_download_models()
