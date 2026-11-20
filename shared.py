"""Models shared by every page, loaded once and cached by Streamlit."""
import streamlit as st

import config


@st.cache_resource(show_spinner="Loading language model...")
def get_sbert():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(config.EMBED_MODEL)


@st.cache_resource(show_spinner=False)
def get_knowledge():
    """Your existing knowledge base: precomputed embeddings and answers (run from the project folder)."""
    import joblib
    return joblib.load("embeddings.pkl"), joblib.load("responses.pkl")


@st.cache_resource(show_spinner="Loading vision model (first run downloads weights)...")
def get_vision():
    from vision_engine import VisionEngine
    return VisionEngine()


@st.cache_resource(show_spinner=False)
def get_analyzer():
    from complaint_logic import ComplaintAnalyzer, TextClassifier
    return ComplaintAnalyzer(TextClassifier(get_sbert()), get_vision())
