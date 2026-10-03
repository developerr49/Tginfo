from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
import duckdb
import os
import requests

app = FastAPI(title="Rahul Telegram Leak API", version="3.1")

# Hugging Face ka Direct Raw File URL yahan daal dein
CSV_URL = "https://huggingface.co/datasets/Rahuldev001/mr-rahuls-portal/resolve/main/Telegram_27.csv"

_db_conn = None

# Database for API Keys
API_KEYS_DB = {
    "rahul_748_free": {"tier": "free", "requests_left": 5},
    "rahul_vip_9999": {"tier": "paid", "requests_left": 999999}
}

def get_duckdb_conn():
    global _db_conn
    if _db_conn is None:
        try:
            print("Connecting to DuckDB and loading CSV directly from URL...")
            _db_conn = duckdb.connect(database=':memory:', read_only=False)
            
            # DuckDB direct URL se stream karke table bana lega bina token ke!
            _db_conn.execute(f"CREATE TABLE leak_data AS SELECT * FROM read_csv_auto('{CSV_URL}')")
            print("Database ready successfully!")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database load error: {str(e)}")
    return _db_conn

@app.get("/api/key-rahul/leak")
def search_leak(q: str = Query(..., description="Telegram Username, ID or Number"), key: str = Query(..., description="API Key")):
    
    # 1. API Key Validation
    if not key or key not in API_KEYS_DB:
        raise HTTPException(status_code=403, detail="Invalid or Unauthorised API Key! Buy from @Mr_Rahul_Dev")
    
    user_data = API_KEYS_DB[key]
    
    # 2. Limit Check for Free Users
    if user_data["tier"] == "free":
        if user_data["requests_left"] <= 0:
            raise HTTPException(status_code=429, detail="Free limit exhausted! Buy unlimited key from @Mr_Rahul_Dev")
        user_data["requests_left"] -= 1

    conn = get_duckdb_conn()
    
    # 3. Search across all columns automatically
    query = f"SELECT * FROM leak_data WHERE CAST(* AS VARCHAR) ILIKE '%{q}%' LIMIT 10"
    
    try:
        df_result = conn.execute(query).fetchdf()
    except Exception as e:
        df_result = conn.execute("SELECT * FROM leak_data LIMIT 1").fetchdf()
    
    results = df_result.to_dict(orient="records")
    
    if not results:
        data_content = {"message": "No data found for this query"}
    else:
        data_content = results

    # 4. Custom Response with your Branding & Credits
    response_payload = {
        "status": True,
        "search_query": q,
        "total_results": len(results),
        "data": data_content,
        "developer_info": {
            "developer": "@Mr_Rahul_Dev",
            "channel": "@Rahuls_Portal",
            "buy_api_from": "@Mr_Rahul_Dev"
        }
    }
    
    return JSONResponse(content=response_payload)

# --- ADMIN ENDPOINT TO GENERATE RANDOM SECURE KEYS ---
@app.get("/admin/generate-key")
def generate_key(admin_secret: str, tier: str = "paid", limit: int = 999999):
    if admin_secret != "rahul_secret_admin_pass":
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    import random
    random_suffix = random.randint(100, 999)
    new_key = f"rahul_{random_suffix}_vip"
    
    API_KEYS_DB[new_key] = {"tier": tier, "requests_left": limit}
    
    return {
        "status": "success",
        "new_api_key": new_key,
        "tier": tier,
        "requests_left": limit
    }
