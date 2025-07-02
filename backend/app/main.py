from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="EORA Chat API", version="1.0.0")

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>EORA Chat</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            h1 { color: #333; }
            .status { color: green; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>🚂 Welcome to EORA Chat!</h1>
        <p>This is your Railway-deployed FastAPI application.</p>
        <p class="status">✅ Status: Running successfully on Railway</p>
        <p>API Documentation: <a href="/docs">/docs</a></p>
    </body>
    </html>
    """

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "EORA Chat API"}

@app.get("/api/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}!", "service": "EORA Chat API"} 