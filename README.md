# TDS Data Analyst Agent

This project is a **data analysis automation agent** that takes natural language questions and:
- Detects the task type (films, sales, weather, network, generic analysis, etc.).
- Loads relevant data from CSV/YAML or scrapes from web sources.
- Runs Pandas/Numpy/Matplotlib analysis.
- Returns results in structured JSON/JSON-array format for automated evaluation.

## Features
- **Automatic routing** based on question and data type.
- **Wikipedia scraping** for films dataset.
- **Custom plotting utilities** with base64 PNG encoding under file size limits.
- **Evaluation-ready YAML test specs** for rubric-based grading.
- **MIT Licensed** for open-source collaboration.

## Films Task Example
When given:


Scrape the list of highest grossing films from Wikipedia.
Answer:

How many $2 bn movies were released before 2000?

Which is the earliest film that grossed over $1.5 bn?

What's the correlation between the Rank and Peak?

Draw a scatterplot of Rank and Peak along with a dotted red regression line through it.

The system will:
1. Scrape Wikipedia's [List of highest-grossing films](https://en.wikipedia.org/wiki/List_of_highest-grossing_films).
2. Perform calculations.
3. Generate a plot under **100 KB**.
4. Return a JSON array like:
```json
[1, "Titanic (1997)", 0.4857821808388924, "data:image/png;base64,..."]


# Install dependencies
pip install -r requirements.txt

# Start the API server
uvicorn main:app --reload

# Send a POST request with your question
curl -X POST http://127.0.0.1:8000/api/ -H "Content-Type: application/json" \
     -d '{"question": "Scrape the list of highest grossing films from Wikipedia ..."}'
