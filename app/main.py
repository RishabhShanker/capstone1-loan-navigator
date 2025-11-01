from dotenv import load_dotenv
load_dotenv()


from fastapi import FastAPI

app = FastAPI(title="Capstone 1 Supervisor")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"msg": "Capstone 1 — Loan Navigator (hello Cloud Run!)"}

from app.routes.policy import router as policy_router
app.include_router(policy_router)

from app.routes.policy_llm import router as policy_llm_router
app.include_router(policy_llm_router)

from app.routes.whatif import router as whatif_router
app.include_router(whatif_router)

from app.routes.whatif import router as whatif_router
app.include_router(whatif_router)
