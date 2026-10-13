from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn
import os

app = FastAPI(title="Firby Master Spec")

@app.get("/master-spec", response_class=HTMLResponse)
@app.get("/", response_class=HTMLResponse)
async def get_master_spec():
    html_path = "/home/ubuntu/firby/master_spec.html"
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Firby Master Spec 2026</h1>"

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8003)
