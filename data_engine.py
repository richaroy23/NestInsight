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

def clean_data(df, upload_id=None):
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
    
    #Save cleaned data to a new CSV file, namespaced per upload so concurrent
    #uploads don't overwrite each other's cleaned file
    filename = f"{upload_id}_cleaned.csv" if upload_id else "cleaned.csv"
    cleaned_path = f"outputs/cleaned/{filename}"
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

def generate_visuals(df, upload_id=None):
    chart_paths = {}
    prefix = f"{upload_id}_" if upload_id else ""

    numeric_cols = df.select_dtypes(include='number').columns

    if len(numeric_cols) == 0:
        return chart_paths

    # Histogram
    plt.figure(figsize=(8, 6))
    df[numeric_cols[0]].hist()
    histogram_path = f"static/charts/{prefix}histogram.png"
    plt.savefig(histogram_path)
    plt.close()
    chart_paths["histogram"] = histogram_path

    # Boxplot
    plt.figure(figsize=(8, 6))
    sns.boxplot(x=df[numeric_cols[0]])
    boxplot_path = f"static/charts/{prefix}boxplot.png"
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
        scatter_path = f"static/charts/{prefix}scatter.png"
        plt.savefig(scatter_path)
        plt.close()
        chart_paths["scatter"] = scatter_path

    # Heatmap
    corr = df.corr(numeric_only=True)

    if not corr.empty:
        plt.figure(figsize=(10, 8))
        sns.heatmap(corr, annot=True)
        heatmap_path = f"static/charts/{prefix}heatmap.png"
        plt.savefig(heatmap_path)
        plt.close()
        chart_paths["heatmap"] = heatmap_path

    return chart_paths

def forecast_sales(df, upload_id=None, date_col=None, sales_col=None):
    # Use user-provided columns if given; otherwise attempt keyword detection
    # as a fallback so the function still works without user input
    if not date_col:
        for col in df.columns:
            if "date" in col.lower():
                date_col = col
                break

    if not sales_col:
        for col in df.columns:
            if any(k in col.lower() for k in ("sales", "total", "amount", "revenue", "profit")):
                sales_col = col
                break

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

    #Future predictions
    future_days = pd.DataFrame({
        "day_num": range(len(daily_sales), len(daily_sales) + 7)
    })

    predictions = model.predict(future_days)

    forecast_path = f"static/charts/{upload_id}_forecast.png" if upload_id else "static/charts/forecast.png"

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

def _geocode_locations(location_values):
    """
    Geocode a list of unique location strings.
    Returns a dict of {location_string: (lat, lon)} for successful lookups.
    Geocodes unique values only to avoid redundant API calls and rate limiting.
    """
    from geopy.geocoders import Nominatim
    from geopy.exc import GeocoderTimedOut, GeocoderServiceError
    import time

    geolocator = Nominatim(user_agent="nestinsight_mapper")
    cache = {}

    for value in location_values:
        if not value or str(value).strip() == "":
            continue
        key = str(value).strip()
        if key in cache:
            continue
        try:
            loc = geolocator.geocode(key, timeout=5)
            if loc:
                cache[key] = (loc.latitude, loc.longitude)
            time.sleep(1)  # Nominatim rate limit: 1 request per second
        except (GeocoderTimedOut, GeocoderServiceError):
            continue  # Skip locations that fail — don't crash the whole map

    return cache


def generate_map(df, upload_id=None, location_col=None):
    # --- Path 1: user selected a text location column ---
    if location_col and location_col in df.columns:
        unique_locations = df[location_col].dropna().unique().tolist()

        # Cap at 50 unique locations to keep geocoding time reasonable
        unique_locations = unique_locations[:50]

        geo_cache = _geocode_locations(unique_locations)

        if not geo_cache:
            return None  # No locations resolved — skip map silently

        # Build coordinate rows from the cache
        coords = []
        for _, row in df.iterrows():
            key = str(row[location_col]).strip()
            if key in geo_cache:
                lat, lon = geo_cache[key]
                coords.append((lat, lon, key))

        if not coords:
            return None

        avg_lat = sum(c[0] for c in coords) / len(coords)
        avg_lon = sum(c[1] for c in coords) / len(coords)

        map_obj = folium.Map(location=[avg_lat, avg_lon], zoom_start=4)
        for lat, lon, label in coords:
            folium.Marker([lat, lon], tooltip=label).add_to(map_obj)

        filename = f"{upload_id}_map.html" if upload_id else "map.html"
        map_path = f"static/maps/{filename}"
        map_obj.save(map_path)
        return map_path

    # --- Path 2: fallback — dataset already has Latitude/Longitude columns ---
    if "Latitude" in df.columns and "Longitude" in df.columns:
        map_obj = folium.Map(
            location=[df["Latitude"].mean(), df["Longitude"].mean()],
            zoom_start=5
        )
        for _, row in df.iterrows():
            folium.Marker([row["Latitude"], row["Longitude"]]).add_to(map_obj)

        filename = f"{upload_id}_map.html" if upload_id else "map.html"
        map_path = f"static/maps/{filename}"
        map_obj.save(map_path)
        return map_path

    # --- Path 3: no usable location data ---
    return None

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
    ]

    X = X.drop(columns=drop_cols, errors="ignore")

    # Convert datetime columns into numeric timestamps
    for col in X.columns:
        if "date" in col.lower():
            X[col] = pd.to_datetime(X[col], errors="coerce")
            X[col] = X[col].astype("int64") // 10**9

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
    for column in X.columns:
        # Convert all non-numeric columns
        if not pd.api.types.is_numeric_dtype(X[column]):
            X[column] = X[column].astype(str).fillna("Missing")

            encoded, _ = pd.factorize(X[column])
            X[column] = encoded

    return X


def train_model(df, target_column=None, upload_id=None):
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
        if not pd.api.types.is_numeric_dtype(y):
            y = pd.Series(pd.factorize(y.astype(str))[0])

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
        filename = f"{upload_id}_model.pkl" if upload_id else "model.pkl"
        model_path = f"outputs/{filename}"

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

def business_insights(df, insight_columns=None):
    numeric_cols = list(df.select_dtypes(include="number").columns)

    if not numeric_cols:
        return ["No numeric columns found for business insight extraction."]

    # Use user-selected columns if provided and valid, otherwise fall back
    # to the first two numeric columns so the function always returns something
    if insight_columns:
        selected = [c for c in insight_columns if c in numeric_cols][:2]
    else:
        selected = numeric_cols[:2]

    insights = []
    for col in selected:
        avg_value = round(df[col].mean(), 2)
        max_value = round(df[col].max(), 2)
        min_value = round(df[col].min(), 2)
        insights.append(f"The average {col} is {avg_value}")
        insights.append(f"The highest recorded {col} is {max_value}, and the lowest is {min_value}")

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