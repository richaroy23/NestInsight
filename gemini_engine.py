import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

client = None

if GROQ_API_KEY:
    try:
        client = Groq(api_key=GROQ_API_KEY)
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
            fallback_model = "llama-3.1-8b-instant"
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