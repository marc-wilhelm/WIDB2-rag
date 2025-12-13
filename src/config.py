import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# PFADE
# ============================================================================
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MARKDOWN_FILE_HT = DATA_DIR / "Geschäftsentwicklung_HomeTech.md"
MARKDOWN_FILE_DS = DATA_DIR / "Geschäftsentwicklung_DigitalSolutions.md"
# ============================================================================
# API-KEYS
# ============================================================================
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# ============================================================================
# RAG-KONFIGURATION
# ============================================================================
# Vektordatenbank
CHROMA_DB_PATH = "./data/chroma_db"  # Wird im data/ Ordner erstellt
CHROMA_COLLECTION_NAME = "controlling_berichte"
CHROMA_TEST_DB_PATH = "./data/chroma_test"
CHROMA_TEST_COLLECTION_NAME = "controlling_berichte_test"

# Embedding
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"

# LLM
CLAUDE_MODEL = "claude-sonnet-4-20250514"
CLAUDE_MAX_TOKENS = 2048
CLAUDE_TEMPERATURE = 0.1

# Retrieval
RAG_N_RESULTS = 10  # Anzahl der abzurufenden Chunks
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50