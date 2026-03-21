from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="Reddit Lead Recommendation & Extraction System")

# Register routes
app.include_router(router)

@app.get("/")
def home():
    return {"message": "Reddit Lead Recommendation API is running!"}
