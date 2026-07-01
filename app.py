"""Second Brain — AI-Powered Bookmark Manager.

Run with: uvicorn app:app --reload
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from backend.config import BASE_DIR, get_settings
from backend.database import init_db
from backend.routes import auth, bookmarks, chat, dashboard, search

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and directories on startup."""
    Path(settings.database_url.replace("sqlite:///", "")).parent.mkdir(parents=True, exist_ok=True)
    settings.uploads_dir.mkdir(parents=True, exist_ok=True)
    Path(settings.chroma_persist_dir).mkdir(parents=True, exist_ok=True)
    init_db()
    yield


app = FastAPI(
    title="Second Brain",
    description="AI-Powered Bookmark Manager — Your Personal Knowledge Base",
    version="1.0.0",
    lifespan=lifespan,
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key,
    max_age=settings.session_max_age_days * 24 * 60 * 60,
    same_site="lax",
    https_only=False,
)

# Static files
static_dir = BASE_DIR / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# API routes
app.include_router(auth.router)
app.include_router(bookmarks.router)
app.include_router(search.router)
app.include_router(dashboard.router)
app.include_router(chat.router)


# ── Page routes (serve frontend) ──────────────────────────────────────────────

from fastapi.templating import Jinja2Templates  # noqa: E402

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def _is_authenticated(request: Request) -> bool:
    return request.session.get("user_id") is not None


@app.get("/")
async def home(request: Request):
    if _is_authenticated(request):
        return RedirectResponse(url="/dashboard")
    return RedirectResponse(url="/login")


@app.get("/login")
async def login_page(request: Request):
    if _is_authenticated(request):
        return RedirectResponse(url="/dashboard")
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register")
async def register_page(request: Request):
    if _is_authenticated(request):
        return RedirectResponse(url="/dashboard")
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/dashboard")
async def dashboard_page(request: Request):
    if not _is_authenticated(request):
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "username": request.session.get("username", "User"),
    })


@app.get("/bookmarks")
async def bookmarks_page(request: Request):
    if not _is_authenticated(request):
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("bookmarks.html", {
        "request": request,
        "username": request.session.get("username", "User"),
    })


@app.get("/bookmarks/{bookmark_id}")
async def bookmark_detail_page(request: Request, bookmark_id: int):
    if not _is_authenticated(request):
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("bookmark_detail.html", {
        "request": request,
        "username": request.session.get("username", "User"),
        "bookmark_id": bookmark_id,
    })


@app.get("/save")
async def save_page(request: Request):
    if not _is_authenticated(request):
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("save.html", {
        "request": request,
        "username": request.session.get("username", "User"),
    })


@app.get("/search")
async def search_page(request: Request):
    if not _is_authenticated(request):
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("search.html", {
        "request": request,
        "username": request.session.get("username", "User"),
    })


@app.get("/collections")
async def collections_page(request: Request):
    if not _is_authenticated(request):
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("collections.html", {
        "request": request,
        "username": request.session.get("username", "User"),
    })


@app.get("/analytics")
async def analytics_page(request: Request):
    if not _is_authenticated(request):
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("analytics.html", {
        "request": request,
        "username": request.session.get("username", "User"),
    })


@app.get("/chat")
async def chat_page(request: Request):
    if not _is_authenticated(request):
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("chat.html", {
        "request": request,
        "username": request.session.get("username", "User"),
    })


@app.get("/health")
async def health():
    return {"status": "healthy", "app": "Second Brain", "version": "1.0.0"}
