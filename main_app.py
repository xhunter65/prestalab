from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "ok", "service": "Presta-Lab API", "database": "connected"}

@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "Presta-Lab API", "database": "connected"}