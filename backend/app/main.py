from fastapi import FastAPI

app = FastAPI(
    title="Nouchi Quiz API",
    version="0.1.0",
)


@app.get("/")
def read_root():
    return {
        "message": "Bienvenue sur Nouchi Quiz API",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}
