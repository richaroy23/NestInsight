import os

import pandas as pd

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import seaborn as sns
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, mean_absolute_error, mean_squared_error

os.makedirs("static/charts", exist_ok=True)
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
    histogram_path = "static/charts/histogram.png"
    plt.savefig(histogram_path)
    plt.close()
    chart_paths["histogram"] = histogram_path

    # Boxplot
    plt.figure(figsize=(8, 6))
    sns.boxplot(x=df[numeric_cols[0]])
    boxplot_path = "static/charts/boxplot.png"
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
        scatter_path = "static/charts/scatter.png"
        plt.savefig(scatter_path)
        plt.close()
        chart_paths["scatter"] = scatter_path

    # Heatmap
    corr = df.corr(numeric_only=True)

    if not corr.empty:
        plt.figure(figsize=(10, 8))
        sns.heatmap(corr, annot=True)
        heatmap_path = "static/charts/heatmap.png"
        plt.savefig(heatmap_path)
        plt.close()
        chart_paths["heatmap"] = heatmap_path

    return chart_paths

TARGET_KEYWORDS = [
    "target",
    "label",
    "class",
    "outcome",
    "sale",
    "sales",
    "revenue",
    "profit",
    "amount",
    "total",
    "quantity",
    "units",
    "value",
]


def _select_target_column(df, target_column=None):
    if target_column and target_column in df.columns:
        return target_column

    best_column = df.columns[-1]
    best_score = float("-inf")

    for index, column in enumerate(df.columns):
        column_name = str(column).lower()
        score = 0

        for keyword in TARGET_KEYWORDS:
            if keyword in column_name:
                score += 8 if keyword in {"target", "label", "class", "outcome"} else 5

        if pd.api.types.is_numeric_dtype(df[column]):
            score += 2

        if df[column].nunique(dropna=True) <= 1:
            score -= 100

        if "id" in column_name or "code" in column_name or "sku" in column_name:
            score -= 10

        if index == len(df.columns) - 1:
            score += 1

        if score > best_score:
            best_score = score
            best_column = column

    return best_column


def _is_classification_target(y):
    if y.dtype == "object" or y.dtype == "bool":
        return True

    unique_count = y.nunique(dropna=True)
    if unique_count <= 15 and unique_count <= max(10, len(y) * 0.1):
        return True

    return False


def _prepare_features(X):
    X = X.copy()
    columns_to_drop = []

    for column in X.columns:
        column_name = str(column).lower()
        unique_count = X[column].nunique(dropna=True)
        unique_ratio = unique_count / max(len(X), 1)

        if ("id" in column_name or "code" in column_name or "sku" in column_name) and unique_ratio > 0.6:
            columns_to_drop.append(column)
            continue

        if X[column].dtype == "object" and unique_count > 25:
            top_categories = X[column].value_counts(dropna=False).nlargest(20).index
            X[column] = X[column].where(X[column].isin(top_categories), "Other")

    if columns_to_drop:
        X = X.drop(columns=columns_to_drop)

    categorical_columns = X.select_dtypes(include=["object", "category", "bool"]).columns
    if len(categorical_columns) > 0:
        X = pd.get_dummies(X, columns=list(categorical_columns), drop_first=True)

    return X


def train_model(df, target_column=None):
    try:
        # Check if dataset has enough columns
        if df.shape[1] < 2:
            return {
                "status": "failed",
                "message": "Not enough columns for training"
            }

        selected_target_column = _select_target_column(df, target_column)

        if selected_target_column not in df.columns:
            return {
                "status": "failed",
                "message": "Could not determine a target column for training"
            }

        # Separate features and target using the selected target column
        X = df.drop(columns=[selected_target_column])
        y = df[selected_target_column]

        # Remove rows where target is missing
        valid_rows = y.notnull()
        X = X[valid_rows]
        y = y[valid_rows]

        X = _prepare_features(X)

        # Convert categorical target into labels
        is_classification = _is_classification_target(y)

        if y.dtype == "object" or y.dtype == "bool":
            y = pd.factorize(y)[0]

        # Ensure enough rows after cleaning
        if len(X) < 5 or X.shape[1] == 0:
            return {
                "status": "failed",
                "message": "Not enough valid rows for training"
            }

        if len(y.unique()) < 2:
            return {
                "status": "failed",
                "message": "Target column must contain at least two classes or values"
            }

        # Split dataset
        stratify = None
        if is_classification:
            class_counts = y.value_counts()
            if not class_counts.empty and class_counts.min() >= 2:
                stratify = y

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.2,
            random_state=42,
            stratify=stratify
        )

        # Train model
        if is_classification:
            model = RandomForestClassifier(
                n_estimators=50,
                max_depth=12,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            )
        else:
            model = RandomForestRegressor(
                n_estimators=50,
                max_depth=12,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            )

        model.fit(X_train, y_train)

        # Predictions
        predictions = model.predict(X_test)

        # Calculate score
        if is_classification:
            score = accuracy_score(y_test, predictions)
            metric_name = "Accuracy"
        else:
            score = mean_absolute_error(y_test, predictions)
            metric_name = "MAE"

        # Save model
        model_path = "outputs/model.pkl"
        joblib.dump(model, model_path)
    
        rounded_score = round(score, 2)

        return {
            "status": "success",
            "metric_name": metric_name,
            "metric_value": rounded_score,
            "score": rounded_score,
            "accuracy": rounded_score,
            "target_column": selected_target_column,
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
        avg_value = round(df[col].mean(), 2)
        max_value = round(df[col].max(), 2)
        min_value = round(df[col].min(), 2)

        insights.append(
            f"The average value of {col} is {avg_value}"
        )

        insights.append(
            f"The highest recorded value in {col} is {max_value}"
        )

        insights.append(
            f"The lowest recorded value in {col} is {min_value}"
        )

    return insights