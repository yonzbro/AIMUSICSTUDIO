import os
import sys
import torch
import numpy as np
import librosa
from scipy.io import wavfile
from model_utils import check_and_download_models

# Add RVC lib to path
sys.path.append("/app")
sys.path.append("/app/lib")

from infer.modules.vc.modules import VC

def rvc_infer(
    pth_path, 
    index_path, 
    input_wav_path, 
    output_wav_path, 
    f0_up_key=0, 
    f0_method="rmvpe",
    index_rate=0.75
):
    """
    Core RVC Inference function using the official RVC modules.
    """
    # 0. Ensure base models exist
    check_and_download_models()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    is_half = True if device == "cuda" else False
    
    print(f"[RVC Inference] Loading model {pth_path} on {device}...")
    
    # Initialize VC module
    vc = VC(config=None) # We can pass a config if needed, but None uses defaults
    
    # Load the specific voice profile
    vc.get_vc(pth_path)
    
    # Perform conversion
    # Parameters for vc_single:
    # sid, input_audio_path, f0_up_key, f0_file, f0_method, file_index, file_index2, index_rate, filter_radius, resample_sr, rms_mix_rate, protect
    print(f"[RVC Inference] Converting {input_wav_path} with {f0_method}...")
    
    info, (target_sr, audio_data) = vc.vc_single(
        sid=0,
        input_audio_path=input_wav_path,
        f0_up_key=f0_up_key,
        f0_file=None,
        f0_method=f0_method,
        file_index=index_path,
        file_index2="", # optional second index
        index_rate=index_rate,
        filter_radius=3,
        resample_sr=0, # no resampling
        rms_mix_rate=0.30,
        protect=0.50
    )
    
    if audio_data is not None:
        wavfile.write(output_wav_path, target_sr, audio_data)
        print(f"[RVC] Success: {output_wav_path}")
    else:
        raise RuntimeError(f"RVC conversion failed: {info}")
