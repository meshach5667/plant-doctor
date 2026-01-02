from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    {
        "Message":"Welcome to Plant Doctor API"
    }


