from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from huggingface_hub import hf_hub_download
import duckdb
import random
import os

app = FastAPI(title="Rahul Telegram Leak API", version="3.0")

# Hugging Face configuration
REPO_ID = "Rahudev001/mr-rahuls-portal"
FILENAME = "Telegram_27.csv"

_db_conn = None

# Database for API Keys (Aap yahan apne secure keys store kar sakte hain)
# Format: "api_key": {"tier": "free/paid", "requests_left": limit}
API_KEYS_DB = {
    "rahul_748_free": {"tier": "free", "requests_left": 5},
    "rahul_vip_9999": {"tier": "paid", "requests_left": 999999}
}

def get_duckdb_conn():
    global _db_conn
    if _db_conn is None:
        try:
            print("Downloading/Locating CSV from Hugging Face...")
            file_path = hf_hub_download(repo_id=REPO_ID, filename=FILENAME, repo_type="dataset")
            
            print("Initializing DuckDB engine...")
            _db_conn = duckdb.connect(database=':memory:', read_only=False)
            _db_conn.execute(f"CREATE TABLE leak_data AS SELECT * FROM read_csv_auto('{file_path}')")
            print("Database ready!")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database load error: {str(e)}")
    return _db_conn

@app.get("/api/key-rahul/leak")
def search_leak(q: str = Query(..., description="Telegram Username or User ID or Number"), key: str = Query(..., description="API Key")):
    
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
    
    # 3. Search across all columns automatically (Username, ID, Phone etc.)
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
    if admin_secret != "rahul_secret_admin_pass": # Ise secure rakhna
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    # Random suffix generate karega taaki koi guess na kar sake (jaise rahul_849)
    random_suffix = random.randint(100, 999)
    new_key = f"rahul_{random_suffix}_vip"
    
    API_KEYS_DB[new_key] = {"tier": tier, "requests_left": limit}
    
    return {
        "status": "success",
        "new_api_key": new_key,
        "tier": tier,
        "requests_left": limit
    }
