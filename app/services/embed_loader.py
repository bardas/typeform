"""
Generate and ingest embeddings into Pinecone based on processed text chunks.
"""

import sys
import logging
from pathlib import Path

from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from pinecone import Pinecone, ServerlessSpec
from app.utils.logging import setup_logging
from app.utils.helper_functions import load_data_config

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)


def init_pinecone_client(pine_cfg: dict) -> Pinecone:
    """
    Initialize the Pinecone client.
    :param pine_cfg:  Settings dict containing 'pinecone' section.
    :return: Pinecone client.
    """

    api_key = pine_cfg.get("api_key")
    if not api_key:
        raise KeyError("api_key not set in config.")
    env = pine_cfg.get("environment")
    index_name = pine_cfg.get("index_name")
    dimension = pine_cfg.get("dimension")
    metric = pine_cfg.get("metric")
    if not all([env, index_name, dimension, metric]):
        raise KeyError("Missing fields in pinecone config")

    pc = Pinecone(api_key=api_key, environment=env)

    logger.info(
        f"Creating Pinecone index '{index_name}' (dim={dimension}, metric={metric})"
    )
    pc.create_index(
        name=index_name,
        dimension=dimension,
        metric=metric,
        spec=ServerlessSpec(cloud="aws", region=env),
    )
    return pc


def upsert_embeddings(pc: Pinecone, embedder: HuggingFaceEmbedding) -> None:
    """
    Read processed chunk files, generate embeddings in batches, and upsert to Pinecone.

    :param pc: Pinecone client.
    :param embedder: Embedder model
    :return:
    """

    data_cfg = load_data_config(section="data")
    proc_dir = Path(data_cfg.get("processed_dir"))
    batch_size = 10

    pine_cfg = load_data_config(section="pinecone")

    index_name = pine_cfg.get("index_name")

    index = pc.Index(index_name)

    batch, ids, metas = [], [], []
    for txt in proc_dir.glob("*_chunk_*.txt"):
        try:
            text = txt.read_text(encoding="utf-8")
            vector = embedder._embed([text])[0]
            batch.append(vector)
            ids.append(txt.stem)
            metas.append({"source": txt.stem, "text": text})
        except Exception as e:
            logger.error(f"Embedding error for {txt.name}: {e}")
            continue

        if len(batch) >= batch_size:
            logger.info(f"Upserting batch of {len(batch)} embeddings")
            index.upsert(vectors=list(zip(ids, batch, metas)))
            batch, ids, metas = [], [], []

    # Upsert remaining
    if batch:
        logger.info(f"Upserting final batch of {len(batch)} embeddings")
        index.upsert(vectors=list(zip(ids, batch, metas)))

    logger.success("Embeddings ingested.")


def main() -> None:
    try:
        cfg = load_data_config(section="pinecone")

        # Initialize Pinecone
        pc = init_pinecone_client(cfg)

        # Initialize embedder
        emb_cfg = load_data_config(section="embedding")
        model_name = emb_cfg.get("model")
        embedder = HuggingFaceEmbedding(model_name=model_name)

        upsert_embeddings(pc, embedder)
    except Exception as e:
        logger.critical(f"Fatal error in embed_loader: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
