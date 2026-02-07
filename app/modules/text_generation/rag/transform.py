import re
from typing import Any, AsyncGenerator
import aiofiles
from app.core.config import AppSettings
from app.core.ml import global_ml_store
import torch

async def load(filepath: str, settings: AppSettings) -> AsyncGenerator[str, Any]:
    async with aiofiles.open(filepath, "r", encoding="utf-8") as f:
        while chunk := await f.read(settings.rag_chunk_size):
            yield chunk


def clean(text: str) -> str:
    t = text.replace("\n", " ")
    t = re.sub(r"\s+", " ", t)
    t = re.sub(r"\. ,", "", t)
    t = t.replace("..", ".")
    t = t.replace(". .", ".")
    cleaned_text = t.replace("\n", " ").strip()
    return cleaned_text

def embed(text: str) -> list[float]:
    pipe = global_ml_store.get("embed_model")
    with torch.no_grad():
        # returns shape (1, seq_len, hidden_dim)
        outputs = pipe(text, return_tensors="pt")
        # Mean pooling: (1, hidden_dim)
        embedding = outputs.mean(dim=1)
        # Convert to list: [float, float, ...]
        return embedding[0].tolist()
