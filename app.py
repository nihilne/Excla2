import secrets

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from core.utils.sessions import Session

app = FastAPI()
app.mount(
    "/static",
    StaticFiles(directory="public/static"),
    name="static",
)

config = uvicorn.Config(
    app,
    host="0.0.0.0",
    port=8000,
    log_level="warning",
)

server = uvicorn.Server(config)
templates = Jinja2Templates(directory="public/templates")


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="home/index.html",
    )


if __name__ == "__main__":
    server.run()
