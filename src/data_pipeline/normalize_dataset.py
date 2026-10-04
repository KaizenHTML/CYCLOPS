from pathlib import Path
from typing import Optional
import html
import re
import sys
import time


# Configure Stdout to Avoid Errors With Special Characters on Windows.
stdout_reconfigure = getattr(sys.stdout, "reconfigure", None)
if callable(stdout_reconfigure):
    try:
        stdout_reconfigure(encoding="utf-8")
    except Exception:
        pass



import pandas as pd


# Precompiled Regular Expressions
RE_HTML_TAGS = re.compile(r"<[^>]+>", re.IGNORECASE)
RE_SCRIPTS_STYLES = re.compile(r"<(script|style)[^>]*>.*?</\1>", re.IGNORECASE | re.DOTALL)
RE_URLS = re.compile(
    r"(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|"
    r"www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|"
    r"https?:\/\/[^\s]+|"
    r"http:\/\/[^\s]+)",
    re.IGNORECASE,
)
RE_EMAILS = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b")
RE_IP_ADDRESS = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
RE_PHONE = re.compile(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}\b")
RE_CURRENCY = re.compile(r"[\$€£¥₹]\s*\d+(?:[.,]\d+)?|\b\d+(?:[.,]\d+)?\s*(?:usd|eur|gbp|dolares|euros)\b", re.IGNORECASE)
RE_WHITESPACE = re.compile(r"\s+")
RE_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]")



# Text Unit Cleaning Function
def clean_text(
    text: Optional[str],
    replace_urls: bool = True,
    replace_emails: bool = True,
    replace_ips: bool = True,
    replace_phones: bool = True,
    replace_currencies: bool = False,
    to_lower: bool = False,
    max_char_len: int = 8000,
) -> str:
    
    if text is None or not isinstance(text, str):
        return ""

    cleaned = str(text)


    # Truncating Astronomical Texts
    if len(cleaned) > max_char_len:
        cleaned = cleaned[:max_char_len]

    # Decode HTML Entities
    cleaned = html.unescape(cleaned)

    # Removing Code Embedded in Script Tags
    cleaned = RE_SCRIPTS_STYLES.sub(" ", cleaned)

    # Standardizing URLs
    if replace_urls:
        cleaned = RE_URLS.sub(" [URL] ", cleaned)

    # Removing HTML Tags
    cleaned = RE_HTML_TAGS.sub(" ", cleaned)

    # Replacement of Direct IP Addresses
    if replace_ips:
        cleaned = RE_IP_ADDRESS.sub(" [IP_ADDRESS] ", cleaned)

    # Email Replacement
    if replace_emails:
        cleaned = RE_EMAILS.sub(" [EMAIL] ", cleaned)

    # Phone Number Replacement
    if replace_phones:
        cleaned = RE_PHONE.sub(" [PHONE] ", cleaned)

    # Normalizing Currencies
    if replace_currencies:
        cleaned = RE_CURRENCY.sub(" [CURRENCY] ", cleaned)

    # Removing Invisible Control Characters
    cleaned = RE_CONTROL_CHARS.sub(" ", cleaned)

    # Normalizing Spaces and Line Breaks
    cleaned = RE_WHITESPACE.sub(" ", cleaned).strip()

    # Conversion to lowercase 
    if to_lower:
        cleaned = cleaned.lower()

    return cleaned



# Directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
INPUT_PATH = BASE_DIR / "data" / "processed" / "unified_dataset.csv"
OUTPUT_DIR = BASE_DIR / "data" / "processed"
OUTPUT_PATH = OUTPUT_DIR / "normalized_dataset.csv"


# Function Normalizing 
def run_normalization(
    input_path: Path = INPUT_PATH,
    output_path: Path = OUTPUT_PATH,
    max_char_len: int = 8000,
    min_char_len: int = 5,
) -> pd.DataFrame:

 
    start_time = time.time()
    print("=" * 70)
    print(" [*] Starting Dataset Normalization PIPELINE")
    print("=" * 70)

    # Validating File Existence
    if not input_path.exists():
        raise FileNotFoundError(
            f"File not found: {input_path}. "
            "Run build_unified_dataset.py first."
        )

    # Loading the Dataset
    print(f"[-] Loading dataset from: {input_path}")
    df = pd.read_csv(input_path)
    initial_rows = len(df)
    print(f"[-] Initial records: {initial_rows:,}")

    # Typological Sanitization Against Nulls
    df["text_content"] = df["text_content"].fillna("").astype(str)


    # Cleaning Process
    print("[-] Applying text cleaning.")
    df["clean_text"] = df["text_content"].apply(
        lambda t: clean_text(
            t,
            replace_urls=True,
            replace_emails=True,
            replace_ips=True,
            replace_phones=True,
            replace_currencies=False,
            to_lower=False,
            max_char_len=max_char_len,
        )
    )


    # Generating New Columns
    df["char_count"] = df["clean_text"].str.len()
    df["word_count"] = df["clean_text"].apply(lambda t: len(t.split()))
    df["url_count"] = df["clean_text"].apply(lambda t: t.count("[URL]"))
    df["has_url"] = (df["url_count"] > 0).astype(int)
    df["has_ip"] = df["clean_text"].apply(lambda t: 1 if "[IP_ADDRESS]" in t else 0)


    # Filtering Residual Texts
    print(f"[-] Filtering empty or irrelevant texts (< {min_char_len} characters)...")
    df_valid = df[df["char_count"] >= min_char_len].copy()
    dropped_empty = initial_rows - len(df_valid)


    # Deduplication
    print("[-] Removing duplicate records.")
    before_dedup = len(df_valid)
    df_dedup = df_valid.drop_duplicates(subset=["clean_text", "is_threat"]).copy()
    dropped_duplicates = before_dedup - len(df_dedup)


    # Reordering Columns
    final_cols = [
        "source_dataset",
        "clean_text",
        "is_threat",
        "char_count",
        "word_count",
        "url_count",
        "has_url",
        "has_ip",
    ]
    df_final = df_dedup[final_cols].reset_index(drop=True)


    # Saving to Disk
    output_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"[-] Saving normalized dataset to: {output_path}")
    df_final.to_csv(output_path, index=False, encoding="utf-8")

    # Time and Records Used
    elapsed = round(time.time() - start_time, 2)
    final_rows = len(df_final)


    print("\n" + "=" * 70)
    print(" [OK] Normalization Successfully Completed.")
    print("=" * 70)
    print(f"Initial records         : {initial_rows:,}")
    print(f"Discarded for emptiness : {dropped_empty:,}")
    print(f"Duplicates removed      : {dropped_duplicates:,}")
    print(f"Final records           : {final_rows:,} - Preserved: {round((final_rows/initial_rows)*100, 1)}%")
    print(f"Total execution time    : {elapsed} seconds")
    print("-" * 70)
    print("Final distribution by source and label:")
    summary = pd.crosstab(
        df_final["source_dataset"],
        df_final["is_threat"],
        margins=True,
    ).rename(columns={0: "Legítimo 0", 1: "Amenaza 1"})
    print(summary.to_string())
    print("=" * 70)

    return df_final


if __name__ == "__main__":
    run_normalization()
