# app/services/summarizer.py
from typing import Optional
import os

# TextRank via sumy
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.text_rank import TextRankSummarizer

# Transformer pipeline
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import logging

logger = logging.getLogger(__name__)

# Lazy-loaded transformer pipeline (only if requested)
_TRANSFORMER_PIPELINE = None
_TRANSFORMER_MODEL = os.environ.get("SUMMARIZER_MODEL", "facebook/bart-large-cnn")
_TRANSFORMER_DEVICE = int(os.environ.get("SUMMARIZER_DEVICE", "-1"))  # -1 = cpu, >=0 gpu index


def _get_transformer_pipeline():
    global _TRANSFORMER_PIPELINE
    if _TRANSFORMER_PIPELINE is None:
        try:
            logger.info("Loading transformer summarization pipeline: %s", _TRANSFORMER_MODEL)
            # Auto download model if not present; in production pre-download on build
            _TRANSFORMER_PIPELINE = pipeline(
                "summarization",
                model=_TRANSFORMER_MODEL,
                device=_TRANSFORMER_DEVICE,
            )
        except Exception as e:
            logger.exception("Failed to load transformer pipeline: %s", e)
            raise
    return _TRANSFORMER_PIPELINE


def textrank_summarize(text: str, sentences_count: int = 3) -> str:
    """
    Extractive summarization using TextRank via sumy.
    Returns the top `sentences_count` sentences concatenated.
    """
    if not text or not text.strip():
        return ""
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = TextRankSummarizer()
    # sumy returns sentence objects; join them with spaces
    sentences = summarizer(parser.document, sentences_count)
    return " ".join(str(s) for s in sentences)


def transformer_summarize(text: str, max_length: int = 200, min_length: int = 50) -> str:
    if not text or not text.strip():
        return ""
    pipe = _get_transformer_pipeline()
    # safe truncate to model's max position embeddings
    tokenizer = pipe.tokenizer
    model = pipe.model
    max_pos = getattr(model.config, "max_position_embeddings", None) or 1024
    # reserve some room for decoder/extra tokens
    safe_max_tokens = max_pos - 10
    inputs = tokenizer(text, return_tensors="pt", truncation=False)
    input_ids = inputs["input_ids"][0]
    if input_ids.size(0) > safe_max_tokens:
        input_ids = input_ids[:safe_max_tokens]
        text = tokenizer.decode(input_ids, skip_special_tokens=True, clean_up_tokenization_spaces=True)
    summary_list = pipe(text, max_length=max_length, min_length=min_length, do_sample=False)
    return summary_list[0].get("summary_text", "")


def summarize(
    text: str,
    method: str = "textrank",
    sentences_count: Optional[int] = None,
    max_length: Optional[int] = None,
    min_length: Optional[int] = None,
) -> str:
    """
    Unified summarization interface.
    method: 'textrank' or 'transformer'
    """
    method = (method or "textrank").lower()
    if method == "transformer":
        _max = max_length or 200
        _min = min_length or 50
        return transformer_summarize(text, max_length=_max, min_length=_min)
    else:
        _sent = int(sentences_count or 3)
        return textrank_summarize(text, sentences_count=_sent)