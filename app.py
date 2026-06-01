import secrets

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from core.utils.sessions import Session
from core.utils.oauth import client

app = FastAPI()
app.mount(
    "/static",
    StaticFiles(directory="www/static"),
    name="static",
)

config = uvicorn.Config(
    app,
    host="0.0.0.0",
    port=8000,
    log_level="warning",
)

server = uvicorn.Server(config)
templates = Jinja2Templates(directory="www/templates")


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="home/index.html",
    )


@app.get("/login")
async def login(request: Request):
    sid = Session.get_cookie(request)
    session = await Session.load(sid)
    if not session.is_new:
        return RedirectResponse("/dashboard")
    else:
        _state = secrets.token_hex(32)
        await session.set("state", _state)
        response = RedirectResponse(client.get_auth_url(_state))
        Session.set_cookie(session, response)
        return response


@app.get("/login/confirm")
async def login_confirm(request: Request):
    return "/login/confirm"


@app.get("/logout")
async def logout(request: Request):
    return "/logout"


@app.get("/dashboard")
async def dashboard(request: Request):
    return "/dashboard"


if __name__ == "__main__":
    server.run()
