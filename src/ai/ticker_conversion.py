# src/ai/ticker_conversion.py
import requests
from src.config import TOGETHER_API_KEY, TOGETHER_API_URL, MODEL_NAME


def get_ticker_from_company_name(company_name: str, language: str = "en") -> str:
    """
    משתמש ב-LLM להמרת שם חברה לטיקר.
    אם אין מפתח API, מחזיר את שם החברה באותיות גדולות.
    """
    if not TOGETHER_API_KEY:
        print("TOGETHER_API_KEY not found")
        return company_name.upper()
    
    if language == "he":
        system_prompt = (
            f"אתה מומחה לשוק ההון. מהו הסימול לבורסה של '{company_name}'? "
            "ענה רק עם הסימול המדויק ללא טקסט נוסף, לדוגמה 'תכלת' עבור חברה מסוימת."
        )
    else:
        system_prompt = (
            f"You are a stock market expert. What is the stock ticker for '{company_name}'? "
            "Return only the exact ticker without any additional text or explanation (e.g., 'AAPL')."
        )
    
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
        ],
        "temperature": 0,
        "max_tokens": 20
    }
    
    try:
        response = requests.post(TOGETHER_API_URL, headers=headers, json=payload)
        response_json = response.json()
        # הדפסת הפלט לצורך דיבאגינג (ניתן להסיר בהמשך)
        print(response_json)
        if "choices" in response_json:
            ticker = response_json["choices"][0]["message"]["content"].strip()
            return ticker.upper()
        else:
            return company_name.upper()
    except Exception as e:
        print(e)
        return company_name.upper()
    
if __name__ == '__main__':
    test_company = "Apple"
    ticker = get_ticker_from_company_name(test_company, language="en")
    print(f"Ticker for '{test_company}': {ticker}")




