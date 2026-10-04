import argparse
import functools
import logging
from pathlib import Path
import re
from typing import Set
import pandas as pd


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
PROCESSED_DIR = DATA_DIR / "processed"
DEFAULT_INPUT_FILE = PROCESSED_DIR / "normalized_dataset.csv"
DEFAULT_OUTPUT_FILE = PROCESSED_DIR / "clean_dataset.csv"


# Precompiled Patterns Specific to NLP and Emergency Care
REGEX_PUNCTUATION = re.compile(r'[^\w\s]')
REGEX_DIGITS = re.compile(r'\d+')
REGEX_WORD_TOKENS = re.compile(r'\b[a-zA-ZáéíóúñÁÉÍÓÚÑ0-9_-]+\b')



# Social Engineering Vocabulary
URGENCY_KEYWORDS: set[str] = {
    "urgent", "urgently", "urgency", "immediate", "immediately", "instant",
    "instantly", "action", "act", "now", "critical", "alert", "warning", "warn",
    "hurry", "deadline", "fast", "quick", "promptly", "limited", "expires",
    "expired", "expiring", "expiration", "today", "final", "notice",
    "urgente", "urgencia", "inmediato", "inmediatamente", "critico", "alerta",
    "aviso", "advertencia", "expira", "vence", "vencimiento", "plazo",
    "suspend", "suspended", "suspension", "terminate", "terminated", "termination",
    "deactivate", "deactivated", "deactivation", "cancel", "cancelled", "cancellation",
    "close", "closed", "block", "blocked", "blocking", "restrict", "restricted",
    "restriction", "lock", "locked", "freeze", "frozen", "penalty", "penalties",
    "fine", "fined", "fines", "legal", "lawsuit", "police", "investigation",
    "arrest", "consequence", "violation", "breach", "compromised", "fraud",
    "unauthorized", "unusual", "suspicious", "fail", "failed", "failure",
    "danger", "risk", "threat", "threats",
    "suspender", "suspendida", "suspendido", "cancelar", "cancelado",
    "bloquear", "bloqueado", "bloqueada", "bloqueo", "multa", "sancion",
    "policia", "infraccion", "violacion", "comprometido", "comprometida",
    "fraude", "sospechoso", "sospechosa", "peligro", "riesgo", "amenaza",
    "verify", "verification", "verified", "validate", "validation", "confirm",
    "confirmation", "update", "authenticate", "authentication", "login", "logon",
    "password", "credentials", "banking", "billing", "invoice", "refund",
    "payment", "overdue", "debt", "settlement", "claim", "winner", "prize",
    "security", "attention", "re-activate",
    "verificar", "verificacion", "validar", "confirmar", "confirmacion",
    "actualizar", "actualizacion", "clave", "contraseña", "banco", "bancario",
    "bancaria", "cuenta", "seguridad", "atencion", "reclamar", "premio"
}

# STOPWORDS Vocabulary
DEFAULT_STOPWORDS: set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't",
    "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't",
    "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i",
    "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's",
    "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself",
    "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought",
    "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she",
    "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves",
    "then", "there", "there's", "these", "they", "they'd", "they'll", "they're",
    "they've", "this", "those", "through", "to", "too", "under", "until", "up",
    "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which",
    "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would",
    "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
    "yourself", "yourselves", "subject"
}



# Preparing the Tools Tokenization and Lemmatization
def _initialize_nlp_components():
    stop_words = set(DEFAULT_STOPWORDS)
    lemmatize_fn = lambda word: word

    try:
        import nltk  
        from nltk.corpus import stopwords  
        WordNetLemmatizer = nltk.stem.WordNetLemmatizer

        for resource in ["stopwords", "wordnet", "omw-1.4"]:
            try:
                nltk.data.find(f"corpora/{resource}")
            except LookupError:
                nltk.download(resource, quiet=True)

        try:
            stop_words = set(stopwords.words("english")).union(DEFAULT_STOPWORDS)
        except LookupError as exc:
            logger.warning("NLTK stopwords not available: %s", exc)
        lemmatizer = WordNetLemmatizer()

        @functools.lru_cache(maxsize=200000)
        def _cached_lemmatize(word: str) -> str:
            return lemmatizer.lemmatize(word)

        lemmatize_fn = _cached_lemmatize
        logger.info("NLTK components loaded successfully.")

    except ImportError:
        logger.warning("NLTK not available. Using default lemmatization..")

    return stop_words, lemmatize_fn


STOPWORDS_SET, LEMMATIZE_FUNC = _initialize_nlp_components()



# Tokenization and Lemmatization Function
def tokenize_and_lemmatize(text: str) -> str:
    if not isinstance(text, str) or pd.isna(text):
        return ""
    content = text.lower()
    content = REGEX_PUNCTUATION.sub(" ", content)
    content = REGEX_DIGITS.sub(" ", content)
    tokens = content.split()
    cleaned_tokens = [
        LEMMATIZE_FUNC(token)
        for token in tokens
        if token not in STOPWORDS_SET and len(token) > 1
    ]
    # List of Lemmatized Tokens
    return " ".join(cleaned_tokens)


# Urgency Score Extraction Function
def extract_urgency_score(text: str) -> float:
    if not isinstance(text, str) or pd.isna(text):
        return 0.0
    words = REGEX_WORD_TOKENS.findall(text.lower())
    if not words:
        return 0.0
    urgency_hits = sum(1 for w in words if w in URGENCY_KEYWORDS)
    return round(urgency_hits / len(words), 4)



def process_dataset(
    input_path: Path = DEFAULT_INPUT_FILE,
    output_path: Path = DEFAULT_OUTPUT_FILE
) -> pd.DataFrame:
    if not input_path.exists():
        logger.warning(f"Not found '{input_path}'. Running normalization first.")
        from src.data_pipeline.normalize_dataset import run_normalization
        run_normalization()

    logger.info(f"Loading normalized dataset from: {input_path}")
    df = pd.read_csv(input_path)

    clean_texts = df["clean_text"].fillna("").astype(str)


    # Generating New Columns
    df["urgency_score"] = [extract_urgency_score(t) for t in clean_texts]
    df["clean_text"] = [tokenize_and_lemmatize(t) for t in clean_texts]

    # Reordering Columns 
    ordered_columns = [
        "source_dataset",
        "clean_text",
        "char_count",
        "word_count",
        "url_count",
        "has_url",
        "has_ip",
        "urgency_score",
        "is_threat",
    ]
    df = df[ordered_columns]

    # Saving the Unified Dataset
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding="utf-8")

    print("\n" + "=" * 60)
    print("Feature Engineering and NLP Summary")
    print("=" * 60)
    print(f"File generated:      {output_path}")
    print(f"Total records:       {len(df)}")
    print(f"Average Urgency:      {df['urgency_score'].mean():.4f}")
    print("=" * 60 + "\n")

    return df


def main():
    parser = argparse.ArgumentParser(description="Feature Engineering and NLP for CYCLOPS.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT_FILE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_FILE)
    args = parser.parse_args()
    process_dataset(input_path=args.input, output_path=args.output)


if __name__ == "__main__":
    main()