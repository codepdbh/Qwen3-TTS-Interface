import os

import torch


def get_default_device() -> str:
    """Devuelve CPU por defecto y deja preparado un override futuro."""
    forced_device = os.getenv("QWEN3_TTS_DEVICE")
    if forced_device:
        return forced_device
    return "cpu"


def is_cuda_available() -> bool:
    return torch.cuda.is_available()


def get_preferred_dtype(device: str) -> torch.dtype:
    if device.startswith("cuda") and is_cuda_available():
        return torch.bfloat16
    return torch.float32

