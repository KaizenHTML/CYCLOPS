from pathlib import Path
import pandas as pd


# Directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def process_corporate_emails(filepath):
    df = pd.read_csv(filepath)
    df = df.rename(columns={"text": "text_content", "label_num": "is_threat"})
    df["source_dataset"] = "corporate_emails"

    return df[["source_dataset", "text_content", "is_threat"]]


def process_phishing_emails(filepath):
    df = pd.read_csv(filepath)
    df = df.rename(columns={"text_combined": "text_content", "label": "is_threat"})
    df["source_dataset"] = "phishing_emails"

    return df[["source_dataset", "text_content", "is_threat"]]


def process_sms_spam(filepath):
    df = pd.read_csv(filepath)
    label_map = {"ham": 0, "spam": 1}
    df["is_threat"] = df["label"].map(label_map)
    df = df.rename(columns={"message": "text_content"})
    df["source_dataset"] = "sms_spam"

    return df[["source_dataset", "text_content", "is_threat"]]



def main():
    print("Initiating dataset ingestion and schema unification...")

    # Applying the Functions
    corp_df = process_corporate_emails(RAW_DIR / "corporate_emails.csv")
    phish_df = process_phishing_emails(RAW_DIR / "phishing_emails.csv")
    sms_df = process_sms_spam(RAW_DIR / "sms_spam.csv")

    # Merging the Datasets
    unified_df = pd.concat([corp_df, phish_df, sms_df], ignore_index=True)

    # Reordering Columns 
    columns_order = ["source_dataset", "text_content", "is_threat"]
    unified_df = unified_df[columns_order]

    # Saving the Unified Dataset
    output_path = PROCESSED_DIR / "unified_dataset.csv"
    unified_df.to_csv(output_path, index=False, encoding="utf-8")

    print("--------------------------------------------------")
    print(f"Unified dataset generated successfully in: {output_path}")
    print(f"Total consolidated records: {len(unified_df)}")
    print("Distribution by original source:")
    print(unified_df["source_dataset"].value_counts().to_string())
    print("--------------------------------------------------")


if __name__ == "__main__":
    main()