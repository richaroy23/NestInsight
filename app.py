from flask import Flask, render_template, request, send_file
from data_engine import *
from report_generator import *

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
    df = load_data(filepath)

    #Clean dataset
    df, cleaned_path, cleaning_report = clean_data(df)
    
    #Analysis
    summary = descriptive_analysis(df)
    stats = statistical_analysis(df)
    chart_paths = generate_visuals(df)
    model_result = train_model(df)
    insights = business_insights(df)
    
    #Generate reports
    pdf_path = generate_pdf(summary, stats, insights, model_result, chart_paths)
    docx_path = generate_docx(summary, stats, insights, model_result, chart_paths)
    
    #Render dashboard 
    return render_template(
    "dashboard.html",
    summary=summary,
    stats=stats,
    cleaning_report=cleaning_report,
    model_result=model_result,
    insights=insights,
    chart_paths=chart_paths,
    cleaned_path=cleaned_path,
    pdf_path=pdf_path,
    docx_path=docx_path
)

@app.route('/download/pdf')
def download_pdf():
    return send_file("outputs/reports/report.pdf", as_attachment=True)

@app.route('/download/docx')
def download_docx():
    return send_file("outputs/reports/report.docx", as_attachment=True)

@app.route('/download/cleaned')
def download_cleaned():
    return send_file("outputs/cleaned/cleaned.csv", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)