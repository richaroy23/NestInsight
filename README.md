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
│── gemini_engine.py
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
│   └── map.html
│
├── static/
│   ├── css/
│   │   ├── style.css
│   │   └── dashboard.css
│   │
│   ├── js/
│   │   └── dashboard.js
│   │
│   └── charts/
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
SUPABASE_KEY=your_supabase_key
SECRET_KEY=your_secret_key
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.1-8b-instant
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

---

## Future Improvements

* Advanced forecasting models (Prophet, ARIMA)
* Advanced charts (Sankey, Sunburst)
* A/B testing preparation
* Data lake integrations
* Team collaboration
* Excel export
* Background job queues
* Real-time dashboard updates

---
For ReadyNest Internship Week 1
