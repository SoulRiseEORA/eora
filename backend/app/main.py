from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/")
def read_root():
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>EORA Chat</title>
    </head>
    <body>
        <h1>Hello from EORA!</h1>
        <p>This is your Railway-deployed FastAPI app.</p>
        <p>Status: Working!</p>
    </body>
    </html>
    """)

@app.get("/health")
def health_check():
    return {"status": "healthy"} 