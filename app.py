import os
import uuid
import json

from flask import Flask, render_template, request, send_file, session, redirect
from markupsafe import Markup
import markdown
from werkzeug.utils import secure_filename
from data_engine import *
from report_generator import *
from groq_engine import generate_ai_insights

try:
    from supabase_client import supabase
except Exception:
    supabase = None

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")
if not _secret_key:
    import warnings
    warnings.warn(
        "SECRET_KEY env var is not set — falling back to an insecure default. "
        "Set SECRET_KEY in your Render environment variables before going live.",
        stacklevel=2
    )
    _secret_key = "supersecret"
app.secret_key = _secret_key

app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024

os.makedirs("uploads", exist_ok=True)
os.makedirs("outputs/cleaned", exist_ok=True)
os.makedirs("outputs/reports", exist_ok=True)


def allowed_file(filename):
    return bool(filename) and filename.lower().endswith(".csv")


def upload_to_supabase(local_path, bucket_folder, filename, download_name=None):
    if supabase is None or not local_path or not os.path.exists(local_path):
        return None

    with open(local_path, "rb") as f:
        supabase.storage.from_("nestinsight-files").upload(
            f"{bucket_folder}/{filename}",
            f,
            {"upsert": "true", "content-type": "application/octet-stream"}
        )

    # Signed URLs work whether the bucket is public or private.
    # 604800 seconds = 7 days, long enough for a reviewer to download reports
    # without the link expiring mid-session.
    signed = supabase.storage.from_("nestinsight-files").create_signed_url(
        f"{bucket_folder}/{filename}",
        604800,
        {"download": download_name or True}
    )

    # The supabase-py client returns either a dict with a "signedURL" key
    # or an object with a signedURL attribute depending on the version.
    if isinstance(signed, dict):
        return signed.get("signedURL") or signed.get("signedUrl")
    return getattr(signed, "signed_url", None) or getattr(signed, "signedURL", None)

def render_markdown_text(text):
    return Markup(markdown.markdown(text or "", extensions=["extra", "sane_lists"]))

#Signup
@app.route("/signup", methods=["POST"])
def signup():
    if supabase is None:
        return render_template(
            "auth.html",
            error_message="Signup is unavailable right now: the database connection is not configured."
        )

    try:
        email = request.form.get("email")
        password = request.form.get("password")

        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })

        return render_template(
            "auth.html",
            success_message="Signup successful. Please login."
        )

    except Exception as e:
        return render_template(
            "auth.html",
            error_message=str(e)
        )
    
#Login
@app.route("/login", methods=["POST"])
def login():
    if supabase is None:
        return render_template(
            "auth.html",
            error_message="Login is unavailable right now: the database connection is not configured."
        )

    try:
        email = request.form.get("email")
        password = request.form.get("password")

        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        session["user_id"] = response.user.id
        session["email"] = response.user.email

        return redirect("/dashboard")

    except Exception as e:
        return render_template(
            "auth.html",
            error_message=str(e)
        )
    
#Home
@app.route('/')
def home():
    return render_template('auth.html')

@app.route('/dashboard')
def dashboard():
    if "user_id" not in session:
        return redirect("/")

    return render_template("index.html")

#Upload
@app.route('/upload', methods=['POST'])
def upload():
    if "user_id" not in session:
        return redirect("/")
    file = request.files.get("file")

    if file is None or file.filename == "":
        return render_template("index.html", error_message="Please choose a CSV file before uploading."), 400

    if not allowed_file(file.filename):
        return render_template("index.html", error_message="Only .csv files are supported."), 400

    safe_name = secure_filename(file.filename)
    upload_id = uuid.uuid4().hex
    filepath = os.path.join("uploads", f"{upload_id}_{safe_name}")
    file.save(filepath)
    
    #Load dataset
    df = load_data(filepath)

    #Clean dataset
    df, cleaned_path, cleaning_report = clean_data(df, upload_id)
    
    #Analysis
    summary = descriptive_analysis(df)
    stats = df.describe().to_dict()
    chart_paths = generate_visuals(df, upload_id)
    forecast_chart = forecast_sales(df, upload_id)
    if forecast_chart:
        chart_paths["forecast"] = forecast_chart
    map_file = generate_map(df, upload_id)
    target_column = request.form.get("target_column")
    model_result = train_model(df, target_column=target_column, upload_id=upload_id)
    basic_insights = business_insights(df)
    basic_insights.append(model_performance_insight(model_result))
    ai_insights = generate_ai_insights(summary, stats)
    ai_insights_html = render_markdown_text(ai_insights)

    #Generate reports
    pdf_path = generate_pdf(summary, stats, basic_insights, model_result, chart_paths, ai_insights)
    docx_path = generate_docx(summary, stats, basic_insights, model_result, chart_paths, ai_insights)

    cleaned_url = None
    pdf_url = None
    docx_url = None

    if supabase is not None:
        try:
            cleaned_url = upload_to_supabase(cleaned_path, "cleaned", f"{upload_id}_cleaned.csv", download_name="cleaned_data.csv")
            pdf_url = upload_to_supabase(pdf_path, "reports", f"{upload_id}.pdf", download_name="NestInsight_Report.pdf")
            docx_url = upload_to_supabase(docx_path, "reports", f"{upload_id}.docx", download_name="NestInsight_Report.docx")

            supabase.table("reports").insert({
                "user_id": session.get("user_id"),
                "dataset_name": safe_name,
                "target_column": target_column,
                "model_score": model_result.get("metric_value"),
                "cleaned_csv_url": cleaned_url,
                "pdf_url": pdf_url,
                "docx_url": docx_url
            }).execute()
        except Exception as supabase_error:
            print("SUPABASE ERROR:", supabase_error)
            

    if map_file:
        session["last_map_file"] = map_file

    # Persist the analysis context so the results page survives a refresh or
    # a direct URL visit (GET /results/<upload_id>).
    context = {
        "summary": summary,
        "stats": stats,
        "cleaning_report": cleaning_report,
        "model_result": model_result,
        "basic_insights": basic_insights,
        "chart_paths": chart_paths,
        "cleaned_path": cleaned_path,
        "pdf_path": pdf_path,
        "docx_path": docx_path,
        "ai_insights": ai_insights,
        "cleaned_url": cleaned_url,
        "pdf_url": pdf_url,
        "docx_url": docx_url,
        "map_file": map_file,
    }
    context_path = os.path.join("outputs", f"{upload_id}_context.json")
    with open(context_path, "w") as f:
        json.dump(context, f)

    return redirect(f"/results/{upload_id}")

#Results page — stable GET route so refresh / back / shared URLs all work
@app.route("/results/<upload_id>")
def results(upload_id):
    if "user_id" not in session:
        return redirect("/")

    context_path = os.path.join("outputs", f"{upload_id}_context.json")
    if not os.path.exists(context_path):
        return redirect("/dashboard")

    with open(context_path) as f:
        ctx = json.load(f)

    ctx["ai_insights_html"] = render_markdown_text(ctx.get("ai_insights", ""))

    return render_template("dashboard.html", **ctx)

#History page
@app.route("/history")
def history():
    user_id = session.get("user_id")

    if not user_id:
        return redirect("/")

    if supabase is None:
        return render_template(
            "history.html",
            reports=[],
            error_message="History is unavailable right now: the database connection is not configured."
        )

    reports = supabase.table("reports").select("*").eq("user_id", user_id).execute()
    return render_template("history.html", reports=reports.data)

#Map view
@app.route("/map")
def map_view():
    if "user_id" not in session:
        return redirect("/")

    map_path = session.get("last_map_file")

    if not map_path or not os.path.exists(map_path):
        return "No map available for this session.", 404

    return send_file(map_path)

#Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")
    

if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "0") == "1"
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))