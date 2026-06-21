# NestInsight

NestInsight is an AI-powered full-stack data analytics platform that automates the complete analytics pipeline from raw CSV upload to business-ready reports.

It enables users to upload datasets, clean them, perform exploratory analysis, generate machine learning predictions, visualize trends, forecast future performance, and extract AI-powered business intelligence — all in one workflow.

---

## Live Demo

Deployed App: https://nestinsight.onrender.com

GitHub Repository: https://github.com/richaroy23/NestInsight

---

## Features

### Core Analytics Features

* CSV dataset upload
* Dynamic target column selection
* Automatic data cleaning
* Missing value handling
* Duplicate removal
* Cleaned CSV export
* Descriptive statistical analysis
* Dataset summary generation
* Data type inspection
* Missing value report
* Univariate analysis
* Histogram generation
* Boxplot generation
* Bivariate analysis
* Scatterplot generation
* Correlation heatmap
* Interactive dashboard
* KPI cards
* Dashboard chart filters
* Business insights extraction
* Automated numerical insights
* Automatic file encoding detection

---

### Bonus Features

* Feature engineering
* Price × Quantity derived feature
* Time series forecasting (7-day sales prediction)
* Geographic mapping using latitude/longitude
* Automated PDF report generation
* Automated DOCX report generation
* Timestamped report generation

---

### Machine Learning Features

* Automatic target column detection
* Classification model training
* Regression model training
* Random Forest Classifier
* Random Forest Regressor
* Accuracy score evaluation
* Mean Absolute Error evaluation
* Model saving using Joblib
* Dynamic feature preprocessing

---

### AI Intelligence Features

* AI-generated business insights
* Trend detection
* Risk analysis
* Business recommendations
* Strategic analysis using Groq LLM

---

### User Features

* Secure authentication system
* Signup/Login with Supabase Auth
* Protected user sessions
* Personal dashboard
* Analysis history tracking
* Download previous reports

---

### Cloud Features

* Supabase storage integration
* Cleaned dataset cloud upload
* PDF report cloud storage
* DOCX report cloud storage
* User-specific report database

---

## Tech Stack

### Backend

* Flask
* Supabase (Auth + Database + Storage)
* Groq API

---

### Data Processing

* Pandas
* NumPy

---

### Machine Learning

* Scikit-learn
* Joblib

---

### Visualization

* Matplotlib
* Seaborn
* Folium

---

### Reports

* ReportLab (PDF)
* Python-docx (DOCX)

---

### Frontend

* HTML5
* CSS3
* JavaScript

---

### Deployment

* Render
* Gunicorn

---

## Dataset Requirements

NestInsight works with any CSV dataset, but some advanced features are activated only when specific columns are present.

### Minimum Requirement

To perform:
- Data cleaning
- Statistical analysis
- Basic visualizations
- Business insights
- Machine learning training

Your dataset should contain:

- At least **2 columns**
- At least **5 rows**
- A valid **target column** for model training

---

### Optional Advanced Features

| Feature | Required Columns |
|---|---|
| Sales Forecasting | `Transaction Date`, `Total` |
| Geographic Mapping | Any city, state, or country column (or `Latitude` + `Longitude`) |
| Feature Engineering | `Price Per Unit`, `Quantity` |
| Automatic Target Detection | Columns like `sales`, `revenue`, `profit`, `target`, `label`, `class` |

---

### Recommended Dataset Format

For best results:

* Keep column names clear and meaningful
* Avoid empty target columns
* Avoid duplicate rows
* Use numeric values where possible for analysis
* Use proper date formatting for time-based forecasting

---

## Workflow

```text
Authentication
↓
Upload CSV Dataset
↓
Select Target Column
↓
Data Cleaning
↓
Statistical Analysis
↓
Visual Analytics
↓
Forecasting
↓
Geographic Mapping
↓
Machine Learning Training
↓
AI Business Intelligence
↓
Generate Reports
↓
Store Reports in Cloud
↓
Save to History
```

---

## Project Structure

```bash
NestInsight/
│── app.py
│── data_engine.py
│── report_generator.py
│── groq_engine.py
│── supabase_client.py
│── requirements.txt
│── render.yaml
│── README.md
│
├── templates/
│   ├── auth.html
│   ├── index.html
│   ├── dashboard.html
│   ├── history.html
│
├── static/
│   ├── css/
│   │   ├── style.css
│   │   └── dashboard.css
│   │
│   ├── js/
│   │   └── dashboard.js
│   │
│   ├── charts/
│   │
│   └── maps/
│       └── map.html
│
├── uploads/
│
└── outputs/
    ├── cleaned/
    └── reports/
```

---

## Installation

### Clone repository

```bash
git clone https://github.com/richaroy23/NestInsight.git
cd NestInsight
```

---

### Create virtual environment

```bash
python -m venv venv
```

Activate:

Windows:

```bash
venv\Scripts\activate
```

Linux/Mac:

```bash
source venv/bin/activate
```

---

### Install dependencies

```bash
pip install -r requirements.txt
```

---

### Create `.env`

```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_role_key
SECRET_KEY=your_flask_secret_key
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-20b
PORT=5000
```

---

### Run locally

```bash
python app.py
```

Runs on:

```text
http://127.0.0.1:5000
```

---

## Deployment

NestInsight is production-ready and deployed using:

* Render (Flask hosting)
* Supabase (Database/Auth/Storage)

Deployment command:

```bash
gunicorn app:app
```

* Ensure `requirements.txt` includes all dependencies.
* Make sure `render.yaml` is configured correctly.

---

### Supabase Setup

#### Authentication
Enable Email/Password authentication in Supabase Auth.

#### Storage Bucket
Create:

```text
nestinsight-files
```
The bucket can be left **private** — the app uses signed URLs (7-day expiry) so download links work without making the bucket publicly accessible.

#### Database Table

```sql
create table reports (
    id bigint generated by default as identity primary key,
    user_id text,
    dataset_name text,
    target_column text,
    model_score text,
    cleaned_csv_url text,
    pdf_url text,
    docx_url text
);

alter table reports enable row level security;
```

No policies are needed on `reports` — the app only ever accesses it through the Supabase service role key (server-side), which bypasses RLS. Enabling it just blocks anonymous/public access via Supabase's auto-generated REST API.

Also create a `geocache` table. This caches Nominatim geocoding lookups (used by the Geographic Mapping feature) so the same city/state/country strings aren't re-looked-up on every upload — important since Nominatim's usage policy caps requests at 1/second, and re-geocoding common locations on every request risks hitting the Gunicorn worker timeout.

```sql
create table geocache (
    location_name text primary key,
    lat double precision not null,
    lon double precision not null
);

alter table geocache enable row level security;
```

---

### Important Notes

* Render free tier uses temporary storage.
* Reports are stored in Supabase Storage.
* Large uploads are limited to 100MB.
* Missing Groq API key disables AI insights only.

---

### Live Demo Note

The app is hosted on Render's free tier, which spins down after inactivity. If the live demo takes 30–50 seconds to load on first visit, that is normal cold-start behaviour — the app is waking up. Subsequent requests within the same session will be fast.

---

## Deployment Notes

NestInsight is deployed using Render and Supabase. Before deployment, make sure the following setup is completed.

### Render Setup

* Add all required environment variables in Render dashboard.
* Set the start command:

```bash
gunicorn app:app
```
---



## Future Improvements

* Advanced forecasting models (Prophet, ARIMA, LSTM)
* Interactive dashboards with Plotly
* Multi-dataset comparative analytics
* Real-time data streaming support
* Role-based team collaboration
* Automated anomaly detection
* Natural language querying over datasets
* Excel and Power BI export integration
* Background task processing for large datasets
* API access for external integrations

---

For ReadyNest Internship Week 1