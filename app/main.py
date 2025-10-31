from fastapi import FastAPI

app = FastAPI(title="Capstone 1 Supervisor")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"msg": "Capstone 1 — Loan Navigator (hello Cloud Run!)"}
