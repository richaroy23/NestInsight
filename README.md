# NestInsight

NestInsight is an AI-powered dataset intelligence platform that automates the complete analytics pipeline from raw CSV upload to business-ready reports.

It helps users clean data, generate visual insights, train machine learning models, and produce AI-generated business intelligence — all from a single upload.

---

## Features

* User authentication (Signup/Login with Supabase Auth)
* Upload CSV datasets securely
* Automatic data cleaning
* Missing value handling
* Duplicate removal
* Exploratory Data Analysis (EDA)
* Statistical summaries
* Automated chart generation
* Machine learning model training
* Target column selection
* Business insights generation
* AI-generated strategic insights using Groq LLM
* PDF report generation
* DOCX report generation
* Cloud storage for reports using Supabase Storage
* User-specific analysis history
* Download cleaned datasets and reports
* Session-based protected dashboard

---

## Tech Stack

### Backend

* Flask
* Supabase (Auth + Database + Storage)
* Groq API

### Data Processing

* Pandas
* NumPy

### Machine Learning

* Scikit-learn
* Joblib

### Visualization

* Matplotlib
* Seaborn

### Reports

* ReportLab (PDF)
* Python-docx (DOCX)

### Frontend

* HTML
* CSS
* JavaScript

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
│── .gitignore
│── templates/
│   ├── auth.html
│   ├── index.html
│   ├── dashboard.html
│   └── history.html
│── static/
│   ├── css/
│   └── charts/
│── uploads/
│── outputs/
```

---

## Setup (Local)

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd NestInsight
```

### 2. Create virtual environment

```bash
python -m venv .venv
```

Activate:

Windows:

```bash
.venv\Scripts\activate
```

Mac/Linux:

```bash
source .venv/bin/activate
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Create `.env`

Create a `.env` file in root:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
SECRET_KEY=your_secret_key
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.1-8b-instant
```

---

### 5. Run the application

```bash
python app.py
```

Runs at:

```text
http://127.0.0.1:5000
```

---

## Deployment

This project is production-ready for deployment using:

* Render (Flask hosting)
* Supabase (Database/Auth/Storage)

### Render deployment steps:

1. Push code to GitHub
2. Connect repository to Render
3. Add environment variables
4. Deploy

Start command:

```bash
gunicorn app:app
```

---

## Authentication Flow

```text
Auth Page
↓
Login / Signup
↓
Dashboard
↓
Upload CSV
↓
Analysis Dashboard
↓
History Page
↓
Logout
```

---

## Future Improvements

* Background job queue for large datasets
* Better model selection
* More advanced visualizations
* Dataset versioning
* Team collaboration
* Export to Excel
* Advanced forecasting models

