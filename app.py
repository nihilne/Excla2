import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse

app = FastAPI()
app.mount(
    "/static",
    StaticFiles(directory="www/static"),
    name="static",
)
templates = Jinja2Templates(directory="www/templates")

config = uvicorn.Config(
    app,
    host="0.0.0.0",
    port=8000,
    log_level="warning",
)
server = uvicorn.Server(config)


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="home/index.html",
    )


@app.get("/robots.txt")
async def robots():
    return FileResponse("www/static/robots.txt", media_type="text/plain")


@app.get("/sitemap.xml")
async def sitemap():
    return FileResponse("www/static/sitemap.xml", media_type="text/plain")


if __name__ == "__main__":
    server.run()
