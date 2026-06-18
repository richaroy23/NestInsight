import pandas as pd

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

#Load dataset
def load_data(filepath):
    df = pd.read_csv(filepath)
    return df

def clean_data(df):

    missing_before = df.isnull().sum().sum()
    duplicates_before = df.duplicated().sum()

    #Remove duplicates
    df.drop_duplicates(inplace=True)

    #Handle numeric missing values
    for col in df.select_dtypes(include='number').columns:
        df[col] = df[col].fillna(df[col].mean())
    
    #Handle categorical missing values
    for col in df.select_dtypes(include='object').columns:
        if not df[col].mode().empty:
            df[col] = df[col].fillna(df[col].mode()[0])
    
    #Save cleaned data to a new CSV file
    cleaned_path = "outputs/cleaned/cleaned.csv"
    df.to_csv(cleaned_path, index=False)

    cleaning_report = {
        "missing_before": int(missing_before),
        "duplicates_removed": int(duplicates_before)
    }

    return df, cleaned_path, cleaning_report

def descriptive_analysis(df):
    summary = {
    "rows": df.shape[0],
    "columns": df.shape[1],
    "column_names": list(df.columns),
    "data_types": df.dtypes.astype(str).to_dict(),
    "missing_values": df.isnull().sum().to_dict()
}
    return summary

def statistical_analysis(df):
    stats = df.describe(include='all').fillna("N/A").to_dict()
    return stats

def generate_visuals(df):
    chart_paths = {}

    numeric_cols = df.select_dtypes(include='number').columns

    if len(numeric_cols) == 0:
        return chart_paths

    # Histogram
    plt.figure(figsize=(8, 6))
    df[numeric_cols[0]].hist()
    histogram_path = "outputs/charts/histogram.png"
    plt.savefig(histogram_path)
    plt.close()
    chart_paths["histogram"] = histogram_path

    # Boxplot
    plt.figure(figsize=(8, 6))
    sns.boxplot(x=df[numeric_cols[0]])
    boxplot_path = "outputs/charts/boxplot.png"
    plt.savefig(boxplot_path)
    plt.close()
    chart_paths["boxplot"] = boxplot_path

    # Scatterplot
    if len(numeric_cols) >= 2:
        plt.figure(figsize=(8, 6))
        sns.scatterplot(
            x=df[numeric_cols[0]],
            y=df[numeric_cols[1]]
        )
        scatter_path = "outputs/charts/scatter.png"
        plt.savefig(scatter_path)
        plt.close()
        chart_paths["scatter"] = scatter_path

    # Heatmap
    corr = df.corr(numeric_only=True)

    if not corr.empty:
        plt.figure(figsize=(10, 8))
        sns.heatmap(corr, annot=True)
        heatmap_path = "outputs/charts/heatmap.png"
        plt.savefig(heatmap_path)
        plt.close()
        chart_paths["heatmap"] = heatmap_path

    return chart_paths

def train_model(df):
    try:
        # Check if dataset has enough columns
        if df.shape[1] < 2:
            return {
                "status": "failed",
                "message": "Not enough columns for training"
            }

        # Separate features and target (last column as target)
        X = df.iloc[:, :-1]
        y = df.iloc[:, -1]

        # Remove rows where target is missing
        valid_rows = y.notnull()
        X = X[valid_rows]
        y = y[valid_rows]

        # Convert categorical input columns into numeric
        drop_cols = []

        for col in X.select_dtypes(include='object').columns:
            if X[col].nunique() > 50:
                drop_cols.append(col)

        X = X.drop(columns=drop_cols)
        X = pd.get_dummies(X)

        # Convert categorical target into labels
        if y.dtype == "object":
            y = pd.factorize(y)[0]

        # Ensure enough rows after cleaning
        if len(X) < 5:
            return {
                "status": "failed",
                "message": "Not enough valid rows for training"
            }

        # Split dataset
        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.2,
            random_state=42
        )

        # Train model
        model = RandomForestClassifier(
            n_estimators=100,
            random_state=42
        )

        model.fit(X_train, y_train)

        # Predictions
        predictions = model.predict(X_test)

        # Accuracy
        accuracy = accuracy_score(y_test, predictions)

        # Save model
        model_path = "outputs/model.pkl"
        joblib.dump(model, model_path)

        return {
            "status": "success",
            "accuracy": round(accuracy * 100, 2),
            "model_path": model_path
        }

    except Exception as e:
        return {
            "status": "failed",
            "message": str(e)
        }

def business_insights(df):
    insights = []
    for col in df.select_dtypes(include='number').columns:
        insights.append(f"{col} average is {df[col].mean()}")
        insights.append(f"{col} highest is {df[col].max()}")
    return insights
