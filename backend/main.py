from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from backend.chatbot_v2 import ask_database
from backend.security import sanitize_input
import sqlite3

from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# ─── RATE LIMIT ──────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="INGRES Groundwater Chatbot API")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ─── CORS ────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── REQUEST MODELS ───────────────────────────────────────────
class Question(BaseModel):
    question: str

class FilterQuery(BaseModel):
    metric: str
    states: list[str] = []
    years: list[str] = []

# ─── DATABASE CONNECTION ─────────────────────────────────────
def get_db_connection():
    return sqlite3.connect("groundwater.db")

# ─── RAW QUERY EXECUTION (OPTIONAL API) ──────────────────────
def run_query(query):
    conn = sqlite3.connect("groundwater.db")
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return rows

# ─── HOME ────────────────────────────────────────────────────
@app.get("/")
def home():
    return {"message": "INGRES Groundwater Chatbot API Running"}

# ─── SAMPLE ENDPOINT ─────────────────────────────────────────
@app.get("/top_states")
def top_states():
    query = """
    SELECT STATE,
    MAX("Total Ground Water Availability in the area (ham)")
    FROM groundwater
    GROUP BY STATE
    ORDER BY 2 DESC
    LIMIT 10
    """
    result = run_query(query)
    return {"result": result}

# ─── FILTER QUERY ENDPOINT (NEW - DIRECT SQL) ────────────────
@app.post("/filter_query")
@limiter.limit("20/minute")
def filter_query(request: Request, fq: FilterQuery):
    try:
        metric = fq.metric
        states = fq.states
        years = fq.years
        
        # Validate metric
        valid_metrics = [
            "Rainfall (mm) Total",
            "Total Geographical Area (ha) Total",
            "Ground Water Recharge (ham) Total",
            "Annual Ground water Recharge (ham) Total",
            "Annual Extractable Ground water Resource (ham) Total",
            "Ground Water Extraction for all uses (ha.m) Total",
            "Stage of Ground Water Extraction (%) Total",
            "Environmental Flows (ham) Total",
            "Net Annual Ground Water Availability for Future Use (ham) Total",
            "Total Ground Water Availability in the area (ham) Fresh"  # Use Fresh for total availability
        ]
        
        if metric not in valid_metrics:
            raise HTTPException(status_code=400, detail="Invalid metric")
        
        # Determine if metric is STOCK or FLOW
        stock_metrics = [
            "Total Ground Water Availability in the area (ham) Fresh",
            "Net Annual Ground Water Availability for Future Use (ham) Total"
        ]
        
        is_stock = metric in stock_metrics
        
        # Build SQL query
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Base query structure
        if is_stock:
            # For STOCK variables: use latest year or selected year, don't sum across years
            if years:
                # Use selected year(s) - take the latest if multiple
                year_filter = f"AND \"YEAR\" IN ({','.join(['?' for _ in years])})"
                params = years.copy()
            else:
                # Use latest year (2024_25)
                year_filter = "AND \"YEAR\" = '2024_25'"
                params = []
            
            if states:
                state_filter = f"AND UPPER(\"STATE\") IN ({','.join(['?' for _ in states])})"
                params.extend([s.upper() for s in states])
            else:
                state_filter = ""
            
            query = f"""
            SELECT \"STATE\", \"YEAR\", SUM(\"{metric}\") as value
            FROM groundwater
            WHERE \"{metric}\" IS NOT NULL
            {year_filter}
            {state_filter}
            GROUP BY \"STATE\", \"YEAR\"
            ORDER BY value DESC
            """
        else:
            # For FLOW variables: can sum across years and districts
            if years:
                year_filter = f"AND \"YEAR\" IN ({','.join(['?' for _ in years])})"
                params = years.copy()
            else:
                year_filter = ""
                params = []
            
            if states:
                state_filter = f"AND UPPER(\"STATE\") IN ({','.join(['?' for _ in states])})"
                params.extend([s.upper() for s in states])
            else:
                state_filter = ""
            
            query = f"""
            SELECT \"STATE\", SUM(\"{metric}\") as value
            FROM groundwater
            WHERE \"{metric}\" IS NOT NULL
            {year_filter}
            {state_filter}
            GROUP BY \"STATE\"
            ORDER BY value DESC
            """
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            return {
                "success": True,
                "data": [],
                "message": "No data available for the selected query",
                "query_type": "stock" if is_stock else "flow"
            }
        
        # Format results
        formatted_results = []
        for row in results:
            if is_stock:
                formatted_results.append({
                    "state": row[0],
                    "year": row[1],
                    "value": row[2]
                })
            else:
                formatted_results.append({
                    "state": row[0],
                    "value": row[1]
                })
        
        return {
            "success": True,
            "data": formatted_results,
            "metric": metric,
            "query_type": "stock" if is_stock else "flow",
            "message": f"Found {len(formatted_results)} results"
        }
        
    except Exception as e:
        print(f"[filter_query error] {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ─── CHAT ENDPOINT ───────────────────────────────────────────
@app.post("/chat")
@limiter.limit("10/minute")
def chat(request: Request, q: Question):
    try:
        clean_question = sanitize_input(q.question)

        answer = ask_database(clean_question)

        if not answer:
            answer = "No data found."

        return {
            "question": clean_question,
            "answer": answer
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
