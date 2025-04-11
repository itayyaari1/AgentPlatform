# AI Agents Platform

A versatile platform that centralizes various AI-powered agents for different tasks and domains. Currently featuring a Financial Analysis Agent with plans to expand to other specialized AI agents.

## Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python
- **Data Processing**: 
  - Pandas
  - NumPy
  - yfinance (for financial data)
- **Visualization**:
  - Matplotlib
  - Streamlit charts
- **PDF Generation**: FPDF
- **Environment Management**: Python Virtual Environment

## Project Structure

```
FinancialChatbot/
├── app.py                  # Main application entry point
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
├── pages/                  # Streamlit pages
│   └── 1_Smart_Stock_Comparison.py  # Financial Analysis Agent
├── src/                    # Source code
│   ├── agents/            # AI agent implementations
│   ├── config/            # Configuration files
│   └── visualization/     # Chart and visualization utilities
└── venv/                  # Virtual environment (created during setup)
```

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd AgentPlatform
   ```

2. **Create and activate virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

The application will be available at http://localhost:8501

## Adding New Agents

To add a new AI agent to the platform:

1. Create a new Python file in the `src/agents/` directory for your agent implementation
2. Create a new page in the `pages/` directory following the naming convention `X_Agent_Name.py`
3. Implement the agent's functionality in the new page
4. Update the main page (`app.py`) to include the new agent in the list of available agents

Example structure for a new agent:
```python
# pages/X_New_Agent.py
import streamlit as st
from src.agents.new_agent import NewAgent

# Page configuration
st.set_page_config(page_title="New Agent")

# Agent implementation
agent = NewAgent()

# UI and functionality implementation
```

## Environment Variables

Create a `.env` file in the root directory with any necessary environment variables:

```
# Example .env file
API_KEY=your_api_key
OTHER_CONFIG=value
```

## Contributing

1. Create a new branch for your feature
2. Implement your changes
3. Test thoroughly
4. Submit a pull request

## Future Enhancements

- Add more specialized AI agents
- Implement user authentication
- Add data persistence
- Enhance visualization capabilities
- Add more export formats
- Implement real-time updates
