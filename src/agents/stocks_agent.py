# agent.py
import requests
from datetime import date, timedelta
from src.config import TOGETHER_API_KEY, TOGETHER_API_URL, MODEL_NAME
from src.data.stock_data import get_stock_data
from src.analysis.statistics import compute_statistics
from src.utils.pdf_generator import generate_pdf_report
from src.ai.ticker_conversion import get_ticker_from_company_name

class FinancialAgent:
    def __init__(self, language="he"):
        self.language = language

    def _get_ai_analysis(self, summary: str) -> str:
        """
        מתודה פרטית המבצעת ניתוח חכם של הנתונים באמצעות API של Together.
        """
        if not TOGETHER_API_KEY:
            return "Error: TOGETHER_API_KEY not found in environment variables."
    
        if self.language == "he":
            system_prompt = "אתה יועץ פיננסי חכם. ענה בעברית בניתוח מקצועי וידידותי על הנתונים שהוזנו."
            user_prompt = f"הנה נתונים על מניות בטבלה (CSV):\n\n{summary}\n\nנתח את הנתונים והסבר למשתמש את הביצועים והסטטיסטיקות החשובות."
        else:
            system_prompt = "You are a smart financial advisor. Respond in English with a friendly and professional analysis."
            user_prompt = f"Here is a table (CSV) with stock statistics:\n\n{summary}\n\nPlease analyze it and explain the key metrics to the user."
    
        headers = {
            "Authorization": f"Bearer {TOGETHER_API_KEY}",
            "Content-Type": "application/json",
        }
    
        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
    
        try:
            response = requests.post(TOGETHER_API_URL, headers=headers, json=payload)
            response_json = response.json()
            if "choices" in response_json:
                return response_json["choices"][0]["message"]["content"]
            elif "error" in response_json:
                return f"Server error: {response_json['error']}"
            else:
                return f"Unexpected response: {response_json}"
        except Exception as e:
            return f"Error contacting AI: {e}"

    def convert_tickers(self, tickers_input: str) -> list:
        """
        מקבל מחרוזת עם שמות חברות או טיקרים (מופרדים בפסיקים) ומחזיר רשימה של טיקרים,
        באמצעות קריאה תמידית לפונקציה get_ticker_from_company_name.
        """
        raw_entries = [entry.strip() for entry in tickers_input.split(",") if entry.strip()]
        tickers_list = []
        for entry in raw_entries:
            # תמיד לקרוא לפונקציה להמרת שם לטיקר, גם אם הקלט נראה כבר כטיקר.
            converted = get_ticker_from_company_name(entry, language=self.language)
            tickers_list.append(converted)
        return tickers_list


    def analyze_stocks(self, tickers_input: str) -> dict:
        """
        מבצע את תהליך הניתוח עבור המניות:
          - ממיר את הקלט לטיקרים
          - מוריד נתוני מניות עבור שנה אחרונה
          - מחשב סטטיסטיקות
          - מבצע ניתוח חכם באמצעות _get_ai_analysis
          - מייצר דו"ח PDF
          
        מחזיר מילון עם:
          * 'analysis_text': טקסט הניתוח
          * 'stats_table': טבלת הסטטיסטיקות (DataFrame)
          * 'pdf_report': דו"ח PDF (BytesIO)
          * 'price_df': נתוני מניות עבור שנה אחרונה (DataFrame)
        """
        tickers_list = self.convert_tickers(tickers_input)
        start_date = date.today() - timedelta(days=365)
        end_date = date.today()
        price_df = get_stock_data(tickers_list, start_date, end_date)
        if price_df.empty:
            return {"error": "לא נמצאו נתונים לטיקרים שנבחרו או שהתרחשה שגיאה."}
        
        stats = compute_statistics(price_df)
        summary_csv = stats.to_csv(index=True)
        analysis_text = self._get_ai_analysis(summary_csv)
        pdf_report = generate_pdf_report(stats, ai_text=analysis_text)
        
        return {
            "analysis_text": analysis_text,
            "stats_table": stats,
            "pdf_report": pdf_report,
            "price_df": price_df
        }

    def chat_with_agent(self, prompt: str) -> str:
        """
        מאפשר שיחה עם הסוכן לאחר ביצוע הניתוח.
        עונה על השאלה באמצעות _get_ai_analysis.
        """
        return self._get_ai_analysis(prompt)
        
if __name__ == '__main__':
    # דוגמה לבדיקה במצב קונסול
    agent = FinancialAgent(language="he")
    test_input = "השווה Apple, Tesla, Google"
    analysis_result = agent.analyze_stocks(test_input)
    if "error" in analysis_result:
        print(analysis_result["error"])
    else:
        print("תוצאות ניתוח:")
        print(analysis_result["stats_table"])
        print("ניתוח חכם:")
        print(analysis_result["analysis_text"])
        
    # דוגמת שאלה לסוכן:
    question = "מהם הסיכונים בהשקעה במניות אלו?"
    response = agent.chat_with_agent(question)
    print("תשובת הסוכן:")
    print(response)
