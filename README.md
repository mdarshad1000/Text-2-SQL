# 🤖 Natural Language to SQL Query Generator

A Streamlit app that converts English questions into SQL queries using AI models. Simply ask questions about your data and get instant results!

## 🚀 Quick Setup

1. Clone and navigate to the project:
```bash
git clone git@github.com:mdarshad1000/Text-2-SQL.git
cd git@github.com:mdarshad1000/Text-2-SQL.git
```

2. Create `.env` file with your API keys:
```env
OPENAI_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
```

3. Start the app:
```bash
docker compose up -d
```

Visit `http://0.0.0.0:8501` in your browser.

## 💡 How to Use

1. Select an AI model (GPT-4, Llama3.2:latest, or Gemini)
{{ If you want to use the Llama3.2 model, ensure the Ollama server is running. }}
2. Type your question (e.g., "Show me all sales from last month")
3. Click "Generate Results"
4. View your data in tables or charts
5. Download results as CSV if needed

## 🏗️ Code Structure & Documentation


### Folder Structure

```
`Chinook_PostgreSql.sql`: SQL script to create database schema
`Dockerfile`: Docker file to build Docker image
`README.md`: This README file
`app.py`: Main application file
`config.py`: Configuration file for LLM models
`docker-compose.yml`: Docker Compose file to run Docker image
`llm_integration.py`: Abstract base class for LLM integrations
`query_executor.py`: Database executor class
`requirements.txt`: Python dependencies
```

### Classes

#### `LLMQueryGenerator` (Abstract Base Class)
Base class for all AI model integrations.
- `generate_sql_from_nl(db_schema, nl_query)`: Abstract method to convert natural language to SQL

#### `OpenAIQueryGenerator`
Handles GPT-4 integration.
- `__init__(model, sys_prompt, user_prompt)`: Initializes with model settings
- `generate_sql_from_nl(db_schema, nl_query)`: Generates SQL using OpenAI API

#### `OllamaQueryGenerator`
Manages Llama3.2:latest integration.
- `__init__(model, sys_prompt, user_prompt)`: Sets up Ollama configuration
- `generate_sql_from_nl(db_schema, nl_query)`: Generates SQL using Ollama

#### `GeminiQueryGenerator`
Handles Google's Gemini integration.
- `__init__(model, sys_prompt, user_prompt)`: Configures Gemini settings
- `generate_sql_from_nl(db_schema, nl_query)`: Generates SQL using Gemini API

#### `DatabaseExecutor`
Manages database operations.
- `connect()`: Establishes database connection
- `disconnect()`: Closes database connection
- `execute_query(query)`: Runs SQL queries and returns results as DataFrame
- `get_schema_info()`: Returns database structure information

### Workflow

1. **Initialization**
   - App starts and creates `DatabaseExecutor` instance
   - Initializes AI models (GPT-4, Llama3.2, Gemini)

2. **User Interaction**
   - User selects AI model
   - Views database schema
   - Enters natural language question

3. **Query Processing**
   ```
   User Question → AI Model → SQL Query → Database → Results → Visualization
   ```

4. **Data Display**
   - Results shown in table format
   - Optional visualization in charts
   - CSV export available

## 🛠️ Troubleshooting

If something's not working:
1. Check container status: `docker compose ps`
2. View logs: `docker compose logs app`
3. Restart if needed: `docker compose restart`

## 📝 Notes

- Uses Chinook sample database (digital media store data)
- Supports basic data visualization
- Downloads available in CSV format
