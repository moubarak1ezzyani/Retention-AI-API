from fastapi import FastAPI
from app.db.database import engine, Base
from app.api.routers import auth, prediction, utils

# Create tables at startup (safe to run repeatedly)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Retention AI API",
    description="Predict employee attrition risk and generate personalised HR retention plans powered by ML + Gemini.",
    version="1.0.0",
)

# Register routers (paths stay identical to original to ensure no tests break)
app.include_router(auth.router)
app.include_router(prediction.router)
app.include_router(utils.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)