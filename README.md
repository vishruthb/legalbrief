# Legal Brief Analysis MVP
Stanford LLM | Bloomberg Terminal 25 Project

An application that analyzes legal briefs, linking arguments between moving and response briefs using LlamaParse and semantic similarity.

## Features
- Document upload and parsing using LlamaParse
- Semantic linking of arguments between briefs
- Interactive visualization of linked arguments
- Explanation transparency for matches
- Supabase integration for data persistence

## Setup
1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
Create a `.env` file with:
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
LLAMAPARSE_API_KEY=your_llamaparse_key
```

3. Run the application:
```bash
streamlit run app.py
```

## Project Structure
- `app.py`: Streamlit frontend
- `backend/`: Backend API and processing logic
  - `api.py`: FastAPI endpoints
  - `parser.py`: Document parsing with LlamaParse
  - `linker.py`: Semantic linking engine
- `database/`: Supabase integration
  - `db.py`: Database operations
- `utils/`: Utility functions
