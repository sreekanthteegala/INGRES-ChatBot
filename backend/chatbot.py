import os
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent

# Load DB
db = SQLDatabase.from_uri("sqlite:///groundwater.db")

# OpenAI LLM
llm = ChatOpenAI(
    model="gpt-4o-mini",   # or "gpt-4o"
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY")  # safer than hardcoding
)

# SQL Agent
agent_executor = create_sql_agent(
    llm=llm,
    db=db,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=10
)

def ask_database(question: str):

    prompt = f"""
You are a data analyst querying a SQLite groundwater database.

Database table: groundwater

CRITICAL SQL RULE 1: All column names MUST be wrapped in double quotes because they contain spaces and special characters.

CRITICAL SQL RULE 2: STATE values are always UPPERCASE in the database (e.g. 'PUNJAB', 'RAJASTHAN', 'KERALA').
Always convert state names to UPPERCASE in your WHERE clause using UPPER(), like:
WHERE UPPER("STATE") = UPPER('Punjab')

CRITICAL SQL RULE 3: YEAR values use underscores and full years, like '2022_23' becomes '2022_2023', '2016_17' becomes '2016_2017'.
Always search YEAR using LIKE with the first year, like:
WHERE "YEAR" LIKE '2022%'
This handles any format the user types (2022-23, 2022_23, 2022-2023, etc.)

Column names (always use exactly as shown, with double quotes):
- "STATE"
- "DISTRICT"
- "Rainfall (mm)"
- "Ground Water Recharge (ham)"
- "Annual Ground water Recharge (ham)"
- "Total Ground Water Availability in the area (ham)"
- "Annual Extractable Ground water Resource (ham)"
- "Ground Water Extraction for all uses (ha.m)"
- "Stage of Ground Water Extraction (%)"
- "Net Annual Ground Water Availability for Future Use (ham)"
- "Environmental Flows (ham)"
- "Total Geographical Area (ha)"
- "YEAR"

Example of correct queries:

-- User asks: "Show rainfall for Punjab in 2022-23"
SELECT "STATE", "DISTRICT", "Rainfall (mm)", "YEAR"
FROM groundwater
WHERE UPPER("STATE") = UPPER('Punjab')
AND "YEAR" LIKE '2022%';

-- User asks: "Which state has highest ground water availability?"
SELECT "STATE", MAX("Total Ground Water Availability in the area (ham)")
FROM groundwater
GROUP BY "STATE"
ORDER BY 2 DESC
LIMIT 5;

User Question:
{question}

Generate the SQL query using the rules above, execute it, and return the answer clearly.
"""

    response = agent_executor.invoke({"input": prompt})

    return response["output"]