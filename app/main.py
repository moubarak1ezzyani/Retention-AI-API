from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import engine, Base
from app.api.routers import auth, predict, retention, utils
from app.core.config import ORIGIN_FRONTEND 

# Create tables at startup 
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Retention AI API",
    description="Predict employee attrition risk and generate personalised HR retention plans powered by ML + Gemini.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ORIGIN_FRONTEND], # only this frontend will be auth
    allow_credentials=True,
    allow_methods=["*"], # GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],
)

# Register routers 
app.include_router(auth.router)
app.include_router(predict.router)
app.include_router(retention.router)
app.include_router(utils.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)