import torch
from transformers import AutoProcessor, MusicgenForConditionalGeneration
import logging

logger = logging.getLogger(__name__)

class ModelLoader:
    _instance = None
    _is_loaded = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
            cls._instance.processor = None
            cls._instance.model = None
            cls._instance.device = "cuda" if torch.cuda.is_available() else "cpu"
        return cls._instance

    def load(self):
        if not self._is_loaded:
            logger.warning(f"Loading musicgen-small to {self.device}")
            self.processor = AutoProcessor.from_pretrained("facebook/musicgen-small")
            self.model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small")
            self.model.to(self.device)
            self._is_loaded = True
            logger.warning("Model loaded successfully.")
        return self.processor, self.model

def get_model_loader():
    return ModelLoader()
