from ..services.generation_service import load_model
from app.core.ml import global_ml_store


def load_models_at_startup():
    # global_ml_store.load(
    #     "model_1", load_model("Qwen/Qwen2.5-0.5B-Instruct", "text-generation")
    # )
    global_ml_store.load(
        "embed_model",
        load_model(
            "jinaai/jina-embeddings-v2-base-en",
            "feature-extraction",
            trust_remote_code=True,
        ),
    )


def clear_models_at_shutdown():
    global_ml_store.clear()
