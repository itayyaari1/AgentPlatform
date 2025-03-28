import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
TOGETHER_API_URL = "https://api.together.xyz/v1/chat/completions"
MODEL_NAME = "mistralai/Mixtral-8x7B-Instruct-v0.1"

# UI Configuration
BACKGROUND_IMAGE_URL = "https://images.unsplash.com/photo-1517816743773-6e0fd518b4a6?ixlib=rb-1.2.1&auto=format&fit=crop&w=1950&q=80"
BACKGROUND_STYLE = """
    <style>
    .stApp {
        background: url("%s") no-repeat center center fixed;
        background-size: cover;
    }
    [data-testid="stAppViewContainer"] {
        background-color: rgba(0, 0, 0, 0.7);
    }
    </style>
""" % BACKGROUND_IMAGE_URL 