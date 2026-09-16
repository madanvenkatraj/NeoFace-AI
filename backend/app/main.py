from fastapi import FastAPI
app = FastAPI(title="NeoFace AI API")

@app.get("/")
def read_root():
    return {"status": "ok"}
