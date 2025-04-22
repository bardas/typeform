import logging
from pinecone import Index
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from app.utils.logging import setup_logging

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)


def retrieve_context(
    question: str,
    index: Index,
    embedder: HuggingFaceEmbedding,
    k: int = 5,
    similarity_cutoff: float = 0.5,
    starting_text: str = "Context:\n",
    divider: str = "\n\n",
) -> str:
    """
    Retrieve and assemble context for a query from Pinecone.

    :param question: The user's query.
    :param index: Pinecone Index instance.
    :param embedder: HuggingFaceEmbedding instance.
    :param k: Maximum number of chunks to retrieve
    :param similarity_cutoff: Minimum cosine threshold
    :param starting_text: Prefix text before context.
    :param divider: Separator between chunks.
    :return: A concatenated string of context chunks.
    """

    # Embed the question
    try:
        qvec = embedder._embed([question])[0]
    except Exception as e:
        logger.error(f"Embedding error: {e}")
        raise RuntimeError("Failed to embed question")

    # Query Pinecone
    try:
        resp = index.query(
            vector=qvec, top_k=k, include_metadata=True, include_values=False
        )
    except Exception as e:
        logger.error(f"Pinecone query error: {e}")
        raise RuntimeError("Failed to query Pinecone")

    hits = [
        m for m in resp.matches if m.score is not None and m.score >= similarity_cutoff
    ]
    hits = hits[:k]
    logger.info(f"Retrieved {len(hits)} hits")

    context = starting_text
    for m in hits:
        text = m.metadata.get("text", "")
        context += text + divider

    return context
