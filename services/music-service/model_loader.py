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
            logger.warning(f"Loading musicgen-small to {self.device} (float16)")

            # CUDA performance optimization
            if self.device == "cuda":
                torch.backends.cudnn.benchmark = True
                logger.warning(f"VRAM before load: {torch.cuda.memory_allocated() / 1024**2:.1f} MB")

            self.processor = AutoProcessor.from_pretrained("facebook/musicgen-small")
            self.model = MusicgenForConditionalGeneration.from_pretrained(
                "facebook/musicgen-small",
                torch_dtype=torch.float16,
                low_cpu_mem_usage=True
            )
            self.model.to(self.device)
            self._is_loaded = True

            if self.device == "cuda":
                logger.warning(f"VRAM after load: {torch.cuda.memory_allocated() / 1024**2:.1f} MB")
            logger.warning("Model loaded successfully in float16.")
        return self.processor, self.model

def get_model_loader():
    return ModelLoader()
