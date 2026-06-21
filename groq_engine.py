import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# llama-3.1-8b-instant was deprecated by Groq on 2026-06-17.
# openai/gpt-oss-20b is Groq's recommended replacement.
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

client = None

if GROQ_API_KEY:
    try:
        # Bounded so a slow/hanging Groq response can't, on its own, eat
        # most of the Gunicorn worker's request timeout — the rest of the
        # /upload pipeline (geocoding, model training, report generation,
        # Supabase uploads) still needs time after this call returns.
        client = Groq(api_key=GROQ_API_KEY, timeout=20.0)
    except Exception:
        client = None


def generate_ai_insights(summary, stats):
    try:
        if client is None:
            return "AI insights unavailable: set GROQ_API_KEY."

        prompt = f"""
        You are a senior business analyst.

        Analyze this dataset summary and statistical report.

        Dataset Summary:
        {summary}

        Statistical Analysis:
        {stats}

        Generate:
        1. Key business insights
        2. Risks or anomalies
        3. Recommendations
        4. Important trends
        """

        try:
            response = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
        except Exception as model_error:
            # Fallback must be a different model from the primary one, or it
            # offers no real protection if the primary model is unavailable.
            fallback_model = "openai/gpt-oss-120b"
            if GROQ_MODEL == fallback_model:
                raise

            response = client.chat.completions.create(
                model=fallback_model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

        return response.choices[0].message.content

    except Exception as e:
        return f"AI Insight Generation Failed: {str(e)}"