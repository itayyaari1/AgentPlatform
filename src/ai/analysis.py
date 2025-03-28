import requests
from ..config import TOGETHER_API_KEY, TOGETHER_API_URL, MODEL_NAME

def get_ai_analysis(summary: str, language: str = "he") -> str:
    """
    Get AI analysis of the financial data.
    
    Args:
        summary (str): Financial data summary in CSV format
        language (str): Language for the analysis ('he' for Hebrew, 'en' for English)
        
    Returns:
        str: AI-generated analysis
    """
    if not TOGETHER_API_KEY:
        return "Error: TOGETHER_API_KEY not found in environment variables."
    
    # Prepare prompts based on language
    if language == "he":
        system_prompt = "אתה יועץ פיננסי חכם. ענה בעברית בניתוח מקצועי וידידותי על הנתונים שהוזנו."
        user_prompt = f"הנה נתונים על מניות בטבלה (CSV):\n\n{summary}\n\nנתח את הנתונים והסבר למשתמש את הביצועים והסטטיסטיקות החשובות."
    else:
        system_prompt = "You are a smart financial advisor. Respond in English with a friendly and professional analysis."
        user_prompt = f"Here is a table (CSV) with stock statistics:\n\n{summary}\n\nPlease analyze it and explain the key metrics to the user."
    
    # Prepare API request
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