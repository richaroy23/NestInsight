from flask import Flask, render_template, request, send_file
from data_engine import *
from report_generator import *
from gemini_engine import generate_ai_insights

app = Flask(__name__)

#Home
@app.route('/')
def home():
    return render_template('index.html')

#Upload
@app.route('/upload', methods=['POST'])
def upload():

    #get the uploaded file
    file = request.files['file']

    filepath = f"uploads/{file.filename}"
    file.save(filepath)
    
    #Load dataset
    print("Loading dataset...")
    df = load_data(filepath)

    #Clean dataset
    print("Cleaning dataset...")
    df, cleaned_path, cleaning_report = clean_data(df)
    
    #Analysis
    print("Generating summary...")
    summary = descriptive_analysis(df)
    print("Generating stats...")
    stats = df.describe().to_dict()
    print("Generating charts...")
    chart_paths = generate_visuals(df)
    print("Training model...")
    target_column = request.form.get("target_column")
    model_result = train_model(df, target_column=target_column)
    print("Generating business insights...")
    basic_insights = business_insights(df)
    print("Generating AI insights...")
    ai_insights = generate_ai_insights(summary, stats)

    #Generate reports
    print("Generating reports...")
    pdf_path = generate_pdf(summary, stats, basic_insights, model_result, chart_paths, ai_insights)
    docx_path = generate_docx(summary, stats, basic_insights, model_result, chart_paths, ai_insights)
    
    #Render dashboard 
    return render_template(
    "dashboard.html",
    summary=summary,
    stats=stats,
    cleaning_report=cleaning_report,
    model_result=model_result,
    basic_insights=basic_insights,
    chart_paths=chart_paths,
    cleaned_path=cleaned_path,
    pdf_path=pdf_path,
    docx_path=docx_path,
    ai_insights=ai_insights
)

@app.route('/download/pdf')
def download_pdf():
    return send_file("outputs/reports/report.pdf", as_attachment=True)

@app.route('/download/docx')
def download_docx():
    return send_file("outputs/reports/report.docx", as_attachment=True)

@app.route('/download/csv')
def download_cleaned():
    return send_file("outputs/cleaned/cleaned.csv", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)