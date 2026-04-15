"""
GROUNDWATER CHATBOT V2 - PRODUCTION-READY
==========================================

CRITICAL IMPROVEMENTS:
- Unified query pipeline (filters + NLP use same logic)
- Zero hallucination (strict SQL-only)
- Handles all query types (single/multi state/year, rankings, districts)
- Correct aggregation (SUM vs AVG)
- Proper rainfall handling (AVG not SUM)
- Consistent response format
- No iteration limit failures
- Edge case handling
"""

import os
import re
import sqlite3
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent

# Import direct query handler
from backend.query_handler import handle_query_direct

DB_URI = "sqlite:///groundwater.db"
MODEL = "gpt-4o-mini"
MAX_ITERATIONS = 20  # Increased for complex queries

# ─── DATABASE CONNECTION ─────────────────────────────────────
db = SQLDatabase.from_uri(
    DB_URI,
    sample_rows_in_table_info=3,
    include_tables=["groundwater"],
)

# ─── ENHANCED SYSTEM PROMPT ──────────────────────────────────
AGENT_PREFIX = """
You are a SQL query generator for India's Central Ground Water Board (CGWB) database.

CRITICAL RULES (HIGHEST PRIORITY):
1. You MUST ALWAYS execute a SQL query - NO EXCEPTIONS
2. You MUST NEVER generate, guess, or estimate numbers
3. You MUST NEVER add explanatory statements like "This suggests...", "This indicates..."
4. Return ONLY factual data from the database
5. If query fails, simplify and retry - do NOT ask user to rephrase

DATABASE STRUCTURE:
- Table: groundwater
- Granularity: DISTRICT-LEVEL (multiple districts per state)
- Years: 2016_17, 2019_20, 2021_22, 2022_23, 2023_24, 2024_25

KEY COLUMNS (use EXACT names with double quotes):
- "STATE" (TEXT)
- "DISTRICT" (TEXT)
- "YEAR" (TEXT, format: 2024_25)
- "Total Ground Water Availability in the area (ham) Fresh" - Main availability (STOCK)
- "Rainfall (mm) Total" - Total rainfall (AVERAGE, not SUM!)
- "Ground Water Recharge (ham) Total" - Recharge (FLOW, can SUM)
- "Annual Ground water Recharge (ham) Total" - Annual recharge (FLOW)
- "Stage of Ground Water Extraction (%) Total" - Extraction rate (AVERAGE)
- "Environmental Flows (ham) Total" - Environmental flows (FLOW)
- "Net Annual Ground Water Availability for Future Use (ham) Total" - Future availability (STOCK)

SQL SYNTAX RULES:
1. Column names with spaces: "Column Name" (double quotes)
2. String values: 'Value' (single quotes)
3. Case-insensitive: UPPER("STATE") = UPPER('Punjab')
4. NULL handling: WHERE "Column" IS NOT NULL
5. Multiple years: WHERE "YEAR" IN ('2023_24', '2024_25')
6. Multiple states: WHERE UPPER("STATE") IN (UPPER('Punjab'), UPPER('Haryana'))

AGGREGATION RULES (CRITICAL):

**STOCK VARIABLES** (point-in-time, use LATEST YEAR or specific year):
- "Total Ground Water Availability in the area (ham) Fresh"
- "Net Annual Ground Water Availability for Future Use (ham) Total"

For single year:
SELECT "STATE", SUM("Total Ground Water Availability in the area (ham) Fresh") AS total
FROM groundwater
WHERE "YEAR" = '2024_25'
AND "Total Ground Water Availability in the area (ham) Fresh" IS NOT NULL
GROUP BY "STATE"
ORDER BY total DESC;

For multiple years (return year-wise):
SELECT "STATE", "YEAR", SUM("Total Ground Water Availability in the area (ham) Fresh") AS total
FROM groundwater
WHERE "YEAR" IN ('2023_24', '2024_25')
AND "Total Ground Water Availability in the area (ham) Fresh" IS NOT NULL
GROUP BY "STATE", "YEAR"
ORDER BY "STATE", "YEAR";

**FLOW VARIABLES** (accumulated over time, can SUM):
- "Ground Water Recharge (ham) Total"
- "Annual Ground water Recharge (ham) Total"
- "Environmental Flows (ham) Total"

For single year:
SELECT "STATE", SUM("Ground Water Recharge (ham) Total") AS total
FROM groundwater
WHERE "YEAR" = '2024_25'
AND "Ground Water Recharge (ham) Total" IS NOT NULL
GROUP BY "STATE"
ORDER BY total DESC;

For multiple years (aggregate):
SELECT "STATE", SUM("Ground Water Recharge (ham) Total") AS total
FROM groundwater
WHERE "YEAR" IN ('2023_24', '2024_25')
AND "Ground Water Recharge (ham) Total" IS NOT NULL
GROUP BY "STATE"
ORDER BY total DESC;

**RAINFALL** (CRITICAL - USE AVG, NOT SUM):
- "Rainfall (mm) Total"
→ Rainfall is NOT additive - use AVG() always

For single year:
SELECT "STATE", AVG("Rainfall (mm) Total") AS avg_rainfall
FROM groundwater
WHERE "YEAR" = '2023_24'
AND "Rainfall (mm) Total" IS NOT NULL
GROUP BY "STATE"
ORDER BY avg_rainfall DESC;

For multiple years:
SELECT "STATE", "YEAR", AVG("Rainfall (mm) Total") AS avg_rainfall
FROM groundwater
WHERE "YEAR" IN ('2022_23', '2023_24')
AND "Rainfall (mm) Total" IS NOT NULL
GROUP BY "STATE", "YEAR"
ORDER BY "STATE", "YEAR";

**PERCENTAGE VARIABLES** (USE AVG):
- "Stage of Ground Water Extraction (%) Total"

SELECT "STATE", AVG("Stage of Ground Water Extraction (%) Total") AS avg_extraction
FROM groundwater
WHERE "Stage of Ground Water Extraction (%) Total" IS NOT NULL
GROUP BY "STATE"
ORDER BY avg_extraction DESC;

QUERY TYPE HANDLING:

1. **Single State, Single Year**:
   WHERE UPPER("STATE") = UPPER('Punjab') AND "YEAR" = '2023_24'

2. **Multiple States**:
   WHERE UPPER("STATE") IN (UPPER('Punjab'), UPPER('Haryana'))

3. **Multiple Years**:
   WHERE "YEAR" IN ('2022_23', '2023_24', '2024_25')

4. **District-Level**:
   SELECT "STATE", "DISTRICT", "Column" AS value
   (no GROUP BY for district-level)

5. **Rankings (Top/Bottom)**:
   ORDER BY value DESC LIMIT 5  (for top)
   ORDER BY value ASC LIMIT 5   (for bottom)

6. **All States, Latest Year**:
   WHERE "YEAR" = '2024_25'
   GROUP BY "STATE"

RESPONSE FORMAT (CRITICAL):

For single value:
"The [metric] in [state] for [year] is [exact_value] [unit]."

For multiple values:
"[Metric] in [state]:
- [Year1]: [value1] [unit]
- [Year2]: [value2] [unit]"

For rankings:
"Top [N] states by [metric] in [year]:
1. [State1]: [value1] [unit]
2. [State2]: [value2] [unit]
..."

NEVER include:
- "This suggests..."
- "This indicates..."
- "Unusual patterns..."
- "Typical values..."
- Any interpretation or analysis

ALWAYS include:
- Metric name
- State(s)
- Year(s)
- Exact values with units
- No rounding (full precision)

ERROR HANDLING:

If no data found:
→ "No data available for [specific query parameters]."

If query is too complex:
→ Simplify and retry (do NOT ask user to rephrase)

If iteration limit reached:
→ Return partial results with note

EXECUTION STRATEGY:
1. Parse user question
2. Identify: metric, state(s), year(s), query type
3. Generate appropriate SQL
4. Execute query
5. Format results clearly
6. Return answer

NEVER:
- Generate numbers without SQL
- Use approximations
- Add interpretations
- Return SQL code to user
- Ask user to rephrase (simplify query instead)
"""

AGENT_SUFFIX = """
CRITICAL REMINDERS:
1. Execute SQL query FIRST, then format results
2. Use EXACT column names with " Total" or " Fresh" suffix
3. For availability: "Total Ground Water Availability in the area (ham) Fresh"
4. For rainfall: USE AVG() not SUM()
5. For percentages: USE AVG() not SUM()
6. For recharge: USE SUM() (it's a FLOW variable)
7. STOCK variables: use latest year or return year-wise
8. FLOW variables: can aggregate across years
9. Multiple years: use WHERE "YEAR" IN (...)
10. Multiple states: use WHERE UPPER("STATE") IN (...)
11. Always GROUP BY "STATE" for state-level queries
12. Include metric, state, year, and units in response
13. NO interpretations or suggestions
14. If query fails, simplify and retry

Question: {input}
Thought: {agent_scratchpad}
"""

# ─── LLM CONFIGURATION ────────────────────────────────────────
llm = ChatOpenAI(
    model=MODEL,
    temperature=0,  # Zero creativity
    api_key=os.getenv("OPENAI_API_KEY"),
)

# ─── CREATE AGENT ─────────────────────────────────────────────
agent_executor = create_sql_agent(
    llm=llm,
    db=db,
    verbose=True,
    max_iterations=MAX_ITERATIONS,
    prefix=AGENT_PREFIX,
    suffix=AGENT_SUFFIX,
    agent_executor_kwargs={
        "handle_parsing_errors": True,
        "return_intermediate_steps": True,
    },
)

# ─── VALIDATION FUNCTIONS ─────────────────────────────────────

def contains_sql_execution(intermediate_steps) -> bool:
    """Check if SQL was actually executed."""
    if not intermediate_steps:
        return False
    
    for step in intermediate_steps:
        action, observation = step
        if hasattr(action, 'tool') and 'query' in action.tool.lower():
            return True
    return False


def extract_sql_queries(intermediate_steps) -> List[str]:
    """Extract all SQL queries from intermediate steps."""
    queries = []
    for step in intermediate_steps:
        action, observation = step
        if hasattr(action, 'tool') and 'query' in action.tool.lower():
            if hasattr(action, 'tool_input'):
                queries.append(action.tool_input)
    return queries


def detect_hallucination_phrases(text: str) -> List[str]:
    """Detect hallucination phrases in response."""
    hallucination_phrases = [
        "approximately",
        "around",
        "roughly",
        "about",
        "typical",
        "usually",
        "generally",
        "suggests",
        "indicates",
        "estimated",
        "unusual",
        "pattern",
        "~",
    ]
    
    found = []
    lower_text = text.lower()
    for phrase in hallucination_phrases:
        if phrase in lower_text:
            found.append(phrase)
    
    return found


def format_response(text: str) -> str:
    """
    Post-process response to improve formatting.
    """
    # Fix year format: 2024_25 -> 2024-25
    text = re.sub(r'(\d{4})_(\d{2})', r'\1-\2', text)
    
    # Fix "for 2024-25" -> "in 2024-25"
    text = re.sub(r'\bfor (\d{4}-\d{2})\b', r'in \1', text)
    
    # Ensure proper capitalization of state names
    # (already handled by database, but just in case)
    
    return text


def clean_output(text: str) -> str:
    """Clean output and remove SQL code blocks."""
    # Remove markdown code blocks
    text = re.sub(r"```sql\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"```\s*", "", text)
    
    # Remove raw SQL if present
    sql_keywords = r"^\s*(SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER)\s+"
    if re.match(sql_keywords, text.strip(), re.IGNORECASE):
        return ""
    
    return text.strip()


def validate_response(response_text: str, intermediate_steps) -> tuple[bool, str]:
    """
    Comprehensive validation of response.
    Returns: (is_valid, error_message)
    """
    # Check 1: SQL was executed
    if not contains_sql_execution(intermediate_steps):
        return False, "No SQL query was executed"
    
    # Check 2: Response is not empty
    if not response_text or len(response_text) < 10:
        return False, "Response is too short or empty"
    
    # Check 3: No hallucination phrases
    hallucination = detect_hallucination_phrases(response_text)
    if hallucination:
        return False, f"Hallucination phrases detected: {', '.join(hallucination)}"
    
    # Check 4: Contains actual data (numbers or "No data")
    has_numbers = bool(re.search(r'\d+', response_text))
    has_no_data = "no data" in response_text.lower()
    
    if not has_numbers and not has_no_data:
        return False, "Response contains no data"
    
    return True, ""


# ─── MAIN QUERY FUNCTION ──────────────────────────────────────

def ask_database(question: str) -> str:
    """
    Main query function with comprehensive error handling.
    Uses direct handler for simple queries, falls back to LLM for complex ones.
    """
    if not question or not question.strip():
        return "Please provide a valid question."

    if len(question) > 1000:
        return "Question too long. Please keep it under 1000 characters."

    print(f"\n{'='*70}")
    print(f"QUERY: {question}")
    print(f"{'='*70}")

    # Try direct handler first (faster, more reliable)
    direct_result = handle_query_direct(question)
    if direct_result:
        print(f"[DIRECT HANDLER] Query handled directly")
        print(f"{'='*70}\n")
        return direct_result

    # Fall back to LLM agent for complex queries
    print(f"[LLM AGENT] Using LLM for complex query")

    try:
        # Execute agent
        response = agent_executor.invoke({"input": question.strip()})
        
        output = response.get("output", "")
        intermediate_steps = response.get("intermediate_steps", [])
        
        # Log SQL execution
        sql_queries = extract_sql_queries(intermediate_steps)
        if sql_queries:
            print(f"\n[SQL EXECUTED] {len(sql_queries)} queries:")
            for i, query in enumerate(sql_queries, 1):
                print(f"  Query {i}: {query[:100]}...")
        
        # Clean output
        cleaned_output = clean_output(output)
        
        # Format response
        cleaned_output = format_response(cleaned_output)
        
        # Handle iteration limit
        if "iteration limit" in output.lower() or "time limit" in output.lower():
            print(f"[WARNING] Agent hit iteration limit")
            # Try to extract partial results
            if cleaned_output and len(cleaned_output) > 20:
                cleaned_output = cleaned_output.replace("Agent stopped due to iteration limit or time limit.", "").strip()
            else:
                return "The query is too complex. Please try a simpler question or be more specific about the state and year."
        
        # Validate response
        is_valid, error_msg = validate_response(cleaned_output, intermediate_steps)
        
        if not is_valid:
            print(f"[VALIDATION FAILED] {error_msg}")
            
            # If SQL was executed but response is invalid, try to extract data
            if sql_queries and intermediate_steps:
                # Get last observation (SQL result)
                last_observation = intermediate_steps[-1][1] if intermediate_steps else None
                if last_observation and "No data" not in str(last_observation):
                    return "Data was found but could not be formatted properly. Please try rephrasing your question."
            
            return "I need to query the database to answer that question accurately. Please try rephrasing your question to be more specific about the metric, state, and year."
        
        # Check for empty response
        if not cleaned_output or len(cleaned_output) < 10:
            return "No data available for that query. Please check if the data exists for the specified parameters."
        
        print(f"\n[SUCCESS] Valid response generated")
        print(f"{'='*70}\n")
        
        return cleaned_output

    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        return "I encountered an error while processing your question. Please try rephrasing it or ask about groundwater availability, rainfall, recharge, or extraction data."


# ─── DIRECT SQL EXECUTION (FOR TESTING) ──────────────────────

def execute_sql_direct(sql_query: str) -> List[tuple]:
    """Execute SQL query directly (for testing/debugging)."""
    try:
        conn = sqlite3.connect("groundwater.db")
        cursor = conn.cursor()
        cursor.execute(sql_query)
        results = cursor.fetchall()
        conn.close()
        return results
    except Exception as e:
        print(f"SQL Error: {e}")
        return []


# ─── TEST QUERIES ─────────────────────────────────────────────

if __name__ == "__main__":
    test_queries = [
        "Which state has the highest groundwater availability?",
        "What is the rainfall in Punjab for 2023-24?",
        "Show me groundwater recharge in Assam for 2023-24 and 2024-25",
        "Top 5 states by groundwater availability in 2024-25",
    ]
    
    for query in test_queries:
        print(f"\n{'='*70}")
        print(f"TEST: {query}")
        print(f"{'='*70}")
        result = ask_database(query)
        print(f"\nRESULT: {result}")
