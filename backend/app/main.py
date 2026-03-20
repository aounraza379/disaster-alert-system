from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Disaster Alert Backend is running"}
