import os
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import RobustScaler


def demonstrate_scaling():
    dataset_path = os.path.join("data", "processed", "clean_dataset.csv")
    
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"The archive {dataset_path} does not exist.")

    print("Loading dataset.")
    df = pd.read_csv(dataset_path)


    # Selecting Quantitative Variables to Scale
    numeric_cols = ["char_count", "word_count", "url_count", "urgency_score"]
    X_numeric = df[numeric_cols]
    y = df["is_threat"]


    # Strict Train/Test Division
    X_train, X_test, y_train, y_test = train_test_split(
        X_numeric, y, test_size=0.20, random_state=42, stratify=y
    )

    print("\n--- Original values ---")
    print(X_train.head(3))


    # The Scaler Learns Medians and IQRs ONLY From the Training Set.
    scaler = RobustScaler()
    scaler.fit(X_train)


    # Transformation of Train and Test Sets Using the Same Formulas
    X_train_scaled = scaler.transform(X_train)
    X_test_scaled = scaler.transform(X_test)


    # Convert to DataFrame For Clean Console Visualization
    X_train_scaled_df = pd.DataFrame(X_train_scaled, columns=numeric_cols)

    print("\n--- Scaled Values with RobustScaler ---")
    print(X_train_scaled_df.head(3))


    # Save the Trained Scaler as .pkl
    os.makedirs("models", exist_ok=True)
    joblib.dump(scaler, "models/robust_scaler.pkl")
    print("\nTrained RobustScaler saved successfully to 'models/robust_scaler.pkl'.")


if __name__ == "__main__":
    demonstrate_scaling()