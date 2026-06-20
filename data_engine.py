import os

import pandas as pd

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import seaborn as sns
import joblib
import folium

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, mean_absolute_error

os.makedirs("static/charts", exist_ok=True)
os.makedirs("static/maps", exist_ok=True)

#Load dataset
def load_data(filepath):
    encodings = ["utf-8", "latin1", "cp1252", "ISO-8859-1"]

    for encoding in encodings:
        try:
            df = pd.read_csv(filepath, encoding=encoding)
            return df
        except UnicodeDecodeError:
            continue

    raise ValueError("Unable to read CSV file. Unsupported encoding.")

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

def forecast_sales(df):
    date_col = None
    sales_col = None

    #Auto-detect date and sales columns
    for col in df.columns:
        col_lower = col.lower()

        if "date" in col.lower():
            date_col = col

        if (
            "total" in col.lower() 
            or "sales" in col.lower() 
            or "amount" in col.lower()
            or "revenue" in col.lower()
            or "profit" in col.lower()
            or "value" in col.lower()
            or "quantity" in col.lower()
            or "units" in col.lower()
            or "price" in col.lower()
            or "cost" in col.lower()
        ):
            sales_col = col

    #Skip if not found
    if not date_col or not sales_col:
        return None

    #Convert detected date column
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')

    #Remove invalid dates
    df = df.dropna(subset=[date_col])

    #Group sales by detected date columns
    daily_sales = df.groupby(date_col)[sales_col].sum().reset_index()

    #Create numerical timeline
    daily_sales["day_num"] = range(len(daily_sales))

    X = daily_sales[["day_num"]]
    y = daily_sales[sales_col]

    model = LinearRegression()
    model.fit(X, y)

    future_days = pd.DataFrame({
        "day_num": range(len(daily_sales), len(daily_sales) + 7)
    })

    #Future predictions
    future_days = pd.DataFrame({
        "day_num": range(len(daily_sales), len(daily_sales) + 7)
    })

    predictions = model.predict(future_days)

    forecast_path = "static/charts/forecast.png"

    plt.figure(figsize=(8, 6))

    #Actual sales
    plt.plot(
        daily_sales[date_col], 
        daily_sales[sales_col], 
        label="Actual"
    )
    
    #Forecasted sales
    future_dates = pd.date_range(
        start=daily_sales[date_col].max(),
        periods=7
    )

    plt.plot(
        future_dates,
        predictions,
        label="Forecast"
    )

    plt.legend()
    plt.savefig(forecast_path)
    plt.close()

    return forecast_path

def generate_map(df):
    if "Latitude" not in df.columns or "Longitude" not in df.columns:
        return None

    map_obj = folium.Map(
        location=[df["Latitude"].mean(), df["Longitude"].mean()],
        zoom_start=5
    )

    for _, row in df.iterrows():
        folium.Marker(
            [row["Latitude"], row["Longitude"]]
        ).add_to(map_obj)

    map_path = "static/maps/map.html"
    map_obj.save(map_path)

    return map_path

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

    if pd.api.types.is_float_dtype(y):
        return False

    if pd.api.types.is_integer_dtype(y):
        unique_count = y.nunique(dropna=True)
        # Treat integer targets as classes only when cardinality is reasonably small.
        return unique_count <= max(20, int(len(y) * 0.1))

    unique_count = y.nunique(dropna=True)
    if unique_count <= 15 and unique_count <= max(10, len(y) * 0.1):
        return True

    return False


def _prepare_features(X):
    X = X.copy()

    # Drop obvious useless columns manually
    drop_cols = [
        "Transaction ID",
        "Customer ID",
        "Transaction Date"
    ]

    X = X.drop(columns=drop_cols, errors="ignore")

    columns_to_drop = []

    for column in X.columns:
        column_name = str(column).lower()
        unique_count = X[column].nunique(dropna=True)
        unique_ratio = unique_count / max(len(X), 1)

        # Drop ID-like columns dynamically
        if ("id" in column_name or "code" in column_name or "sku" in column_name) and unique_ratio > 0.6:
            columns_to_drop.append(column)
            continue

        # Compress high-cardinality categorical values
        if X[column].dtype == "object" and unique_count > 25:
            top_categories = X[column].value_counts(dropna=False).nlargest(20).index
            X[column] = X[column].where(X[column].isin(top_categories), "Other")

    if columns_to_drop:
        X = X.drop(columns=columns_to_drop)

    # Feature engineering
    if "Price Per Unit" in X.columns and "Quantity" in X.columns:
        X["Price_x_Quantity"] = X["Price Per Unit"] * X["Quantity"]

    # Compact categorical encoding to avoid massive one-hot matrices on wide CSVs
    categorical_columns = X.select_dtypes(include=["object", "category", "bool"]).columns
    for column in categorical_columns:
        encoded, _ = pd.factorize(X[column].astype(str).fillna("Missing"))
        X[column] = encoded

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
        if y.dtype == "object" or y.dtype == "bool":
            y = pd.Series(pd.factorize(y)[0])

        is_classification = _is_classification_target(y)
        
        # Ensure enough rows after cleaning
        if len(X) < 5 or X.shape[1] == 0:
            return {
                "status": "failed",
                "message": "Not enough valid rows for training"
            }

        if len(pd.Series(y).unique()) < 2:
            return {
                "status": "failed",
                "message": "Target column must contain at least two classes or values"
            }

        # Split dataset
        stratify = None
        if is_classification:
            class_counts = pd.Series(y).value_counts()
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
            display_score = round(score * 100, 2)
        else:
            score = mean_absolute_error(y_test, predictions)
            metric_name = "MAE"
            display_score = round(score, 2)

        # Save model
        model_path = "outputs/model.pkl"

        joblib.dump(model, model_path)
            
        return {
            "status": "success",
            "metric_name": metric_name,
            "metric_value": display_score,
            "score": round(score, 2),
            "accuracy": display_score,
            "target_column": selected_target_column,
            "model_path": model_path,
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


def model_performance_insight(model_result):
    if not model_result or model_result.get("status") != "success":
        return "Model training did not complete, so there is no performance score to explain."

    metric_name = model_result.get("metric_name", "Score")
    metric_value = model_result.get("metric_value", model_result.get("accuracy", model_result.get("score", "N/A")))
    target_column = model_result.get("target_column", "the selected field")

    if metric_name == "Accuracy":
        return (
            f"The model predicted {target_column} correctly about {metric_value}% of the time, "
            "so a higher number means the model is making more correct predictions."
        )

    return (
        f"The model's MAE for {target_column} is {metric_value}, which means its predictions are "
        "off by about that amount on average, so lower is better."
    )