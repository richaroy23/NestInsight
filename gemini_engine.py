import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel("gemini-2.0-flash")


def generate_ai_insights(summary, stats):
    try:
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

        response = model.generate_content(prompt)

        return response.text
    except Exception as e:
        return f"AI Insight Generation Failed: {str(e)}"