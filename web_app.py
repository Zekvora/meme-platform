"""
MemePlatform - FastAPI Web Application
Full web interface with API
"""
import os
import uuid
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Request, Form, File, UploadFile, HTTPException, Depends, Query
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

import database_new as db
from config import ADMIN_IDS

# Paths
BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "data" / "uploads"
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# Create directories
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

# Config
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".mp4", ".webm"}

app = FastAPI(title="MemePlatform", version="1.0.0")
app.add_middleware(SessionMiddleware, secret_key=os.environ.get("SECRET_KEY", "supersecretkey123"))

# Static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/data/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# Templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


# ═══════════════════════════════════════════════
# DEPENDENCIES
# ═══════════════════════════════════════════════

async def get_current_user(request: Request) -> Optional[dict]:
    """Get current user from session."""
    token = request.session.get("auth_token")
    if not token:
        return None
    session = await db.get_session(token)
    return session


async def require_auth(request: Request) -> dict:
    """Require authentication."""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


async def require_admin(request: Request) -> dict:
    """Require admin role."""
    user = await require_auth(request)
    if not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


def get_file_type(filename: str) -> str:
    """Determine file type from extension."""
    ext = Path(filename).suffix.lower()
    if ext in {".mp4", ".webm"}:
        return "video"
    elif ext == ".gif":
        return "gif"
    return "image"


# ═══════════════════════════════════════════════
# STARTUP
# ═══════════════════════════════════════════════

@app.on_event("startup")
async def startup():
    """Initialize database on startup."""
    await db.init_db()


# ═══════════════════════════════════════════════
# PUBLIC PAGES
# ═══════════════════════════════════════════════

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, category: int = None, search: str = None, page: int = 1, sort: str = "new"):
    """Home page with meme gallery."""
    user = await get_current_user(request)
    
    limit = 24
    offset = (page - 1) * limit
    
    # Sort mapping
    sort_map = {
        "new": ("created_at", "DESC"),
        "popular": ("likes_count", "DESC"),
        "views": ("views_count", "DESC"),
    }
    sort_by, sort_order = sort_map.get(sort, ("created_at", "DESC"))
    
    memes = await db.get_memes(
        status="approved",
        category_id=category,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit,
        offset=offset
    )
    
    total_count = await db.count_memes(status="approved", category_id=category, search=search)
    total_pages = (total_count + limit - 1) // limit
    
    categories = await db.get_categories()
    stats = await db.get_stats()
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": user,
        "memes": memes,
        "categories": categories,
        "stats": stats,
        "current_category": category,
        "search_query": search,
        "page": page,
        "total_pages": total_pages,
        "sort": sort
    })


@app.get("/meme/{meme_id}", response_class=HTMLResponse)
async def view_meme(request: Request, meme_id: int):
    """View single meme page."""
    user = await get_current_user(request)
    meme = await db.get_meme_by_id(meme_id)
    
    if not meme:
        raise HTTPException(status_code=404, detail="Meme not found")
    
    # Only approved or own memes
    if meme["status"] != "approved":
        if not user or (meme["author_id"] != user.get("id") and not user.get("is_admin")):
            raise HTTPException(status_code=403, detail="Meme not available")
    
    await db.increment_views(meme_id)
    
    user_liked = False
    if user:
        user_liked = await db.has_liked(user["id"], meme_id)
    
    return templates.TemplateResponse("meme.html", {
        "request": request,
        "user": user,
        "meme": meme,
        "user_liked": user_liked
    })


@app.get("/share/{token}", response_class=HTMLResponse)
async def view_shared_meme(request: Request, token: str):
    """View shared meme by token."""
    share = await db.get_share_by_token(token)
    
    if not share:
        raise HTTPException(status_code=404, detail="Share link not found or expired")
    
    return templates.TemplateResponse("shared.html", {
        "request": request,
        "share": share
    })


@app.get("/category/{category_id}", response_class=HTMLResponse)
async def category_page(request: Request, category_id: int, page: int = 1):
    """Category page."""
    return await home(request, category=category_id, page=page)


# ═══════════════════════════════════════════════
# AUTH PAGES
# ═══════════════════════════════════════════════

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page."""
    user = await get_current_user(request)
    if user:
        return RedirectResponse("/", status_code=302)
    
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def login(request: Request, telegram_id: str = Form(...), code: str = Form(...)):
    """Process admin login via Telegram code."""
    try:
        tg_id = int(telegram_id.strip())
    except ValueError:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Неверный Telegram ID"
        })
    
    # Check if user is admin
    if tg_id not in ADMIN_IDS:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Доступ запрещён. Вы не администратор."
        })
    
    # Verify the code
    is_valid = await db.verify_admin_code(tg_id, code)
    
    if not is_valid:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Неверный или истекший код"
        })
    
    # Ensure admin user exists and get it
    user = await db.ensure_admin_user(tg_id)
    
    # Create session
    token = await db.create_session(user["id"])
    request.session["auth_token"] = token
    
    return RedirectResponse("/admin", status_code=302)


@app.get("/logout")
async def logout(request: Request):
    """Logout."""
    token = request.session.get("auth_token")
    if token:
        await db.delete_session(token)
    request.session.clear()
    return RedirectResponse("/", status_code=302)


# ═══════════════════════════════════════════════
# USER PAGES
# ═══════════════════════════════════════════════

@app.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request):
    """Upload meme page."""
    user = await get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=302)
    
    categories = await db.get_categories()
    
    return templates.TemplateResponse("upload.html", {
        "request": request,
        "user": user,
        "categories": categories
    })


@app.post("/upload")
async def upload_meme(
    request: Request,
    title: str = Form(None),
    description: str = Form(None),
    category_id: int = Form(None),
    file: UploadFile = File(...)
):
    """Process meme upload."""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401)
    
    # Validate file
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Недопустимый формат файла")
    
    # Read and check size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Файл слишком большой (макс. 50 МБ)")
    
    # Save file
    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = UPLOAD_DIR / filename
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Create meme record
    file_type = get_file_type(filename)
    meme_id = await db.create_meme(
        author_id=user["id"],
        filename=filename,
        title=title,
        description=description,
        category_id=category_id,
        file_type=file_type,
        file_size=len(content)
    )
    
    return RedirectResponse(f"/my-memes?uploaded=1", status_code=302)


@app.get("/my-memes", response_class=HTMLResponse)
async def my_memes(request: Request, status: str = None):
    """User's memes page."""
    user = await get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=302)
    
    memes = await db.get_user_memes(user["id"], status=status)
    
    return templates.TemplateResponse("my_memes.html", {
        "request": request,
        "user": user,
        "memes": memes,
        "filter_status": status
    })


@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    """User profile page."""
    user = await get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=302)
    
    user_memes = await db.get_user_memes(user["id"])
    approved_count = len([m for m in user_memes if m["status"] == "approved"])
    pending_count = len([m for m in user_memes if m["status"] == "pending"])
    
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user": user,
        "approved_count": approved_count,
        "pending_count": pending_count,
        "total_memes": len(user_memes)
    })


# ═══════════════════════════════════════════════
# ADMIN PAGES
# ═══════════════════════════════════════════════

@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    """Admin dashboard."""
    user = await get_current_user(request)
    if not user or not user.get("is_admin"):
        return RedirectResponse("/login", status_code=302)
    
    stats = await db.get_stats()
    category_stats = await db.get_category_stats()
    pending = await db.get_pending_memes(limit=10)
    
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "user": user,
        "stats": stats,
        "category_stats": category_stats,
        "pending_memes": pending
    })


@app.get("/admin/moderation", response_class=HTMLResponse)
async def admin_moderation(request: Request, page: int = 1):
    """Admin moderation page."""
    user = await get_current_user(request)
    if not user or not user.get("is_admin"):
        return RedirectResponse("/login", status_code=302)
    
    limit = 24
    offset = (page - 1) * limit
    pending = await db.get_memes(status="pending", limit=limit, offset=offset)
    pending_count = await db.count_memes(status="pending")
    
    return templates.TemplateResponse("admin/moderation.html", {
        "request": request,
        "user": user,
        "memes": pending,
        "pending_count": pending_count,
        "page": page
    })


@app.get("/admin/memes", response_class=HTMLResponse)
async def admin_memes(
    request: Request,
    status: str = None,
    category: int = None,
    search: str = None,
    page: int = 1
):
    """Admin all memes page."""
    user = await get_current_user(request)
    if not user or not user.get("is_admin"):
        return RedirectResponse("/login", status_code=302)
    
    limit = 24
    offset = (page - 1) * limit
    
    memes = await db.get_memes(
        status=status,
        category_id=category,
        search=search,
        limit=limit,
        offset=offset
    )
    
    categories = await db.get_categories()
    
    return templates.TemplateResponse("admin/memes.html", {
        "request": request,
        "user": user,
        "memes": memes,
        "categories": categories,
        "filter_status": status,
        "filter_category": category,
        "search_query": search,
        "page": page
    })


@app.get("/admin/categories", response_class=HTMLResponse)
async def admin_categories(request: Request):
    """Admin categories page."""
    user = await get_current_user(request)
    if not user or not user.get("is_admin"):
        return RedirectResponse("/login", status_code=302)
    
    categories = await db.get_category_stats()
    
    return templates.TemplateResponse("admin/categories.html", {
        "request": request,
        "user": user,
        "categories": categories
    })


@app.post("/admin/categories")
async def admin_categories_post(
    request: Request,
    name: str = Form(...),
    icon: str = Form("📁"),
    description: str = Form(None),
    id: int = Form(None)
):
    """Create or update category."""
    user = await get_current_user(request)
    if not user or not user.get("is_admin"):
        return RedirectResponse("/login", status_code=302)
    
    if id:
        await db.update_category(id, name=name, icon=icon, description=description)
    else:
        await db.create_category(name=name, icon=icon, description=description)
    
    return RedirectResponse("/admin/categories", status_code=302)


# ═══════════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════════

@app.post("/api/meme/{meme_id}/approve")
async def api_approve_meme(request: Request, meme_id: int):
    """Approve meme."""
    user = await require_admin(request)
    await db.approve_meme(meme_id, user["id"])
    return {"success": True}


@app.post("/api/meme/{meme_id}/reject")
async def api_reject_meme(request: Request, meme_id: int, reason: str = Form(None)):
    """Reject meme."""
    user = await require_admin(request)
    await db.reject_meme(meme_id, user["id"], reason)
    return {"success": True}


@app.delete("/api/meme/{meme_id}")
async def api_delete_meme(request: Request, meme_id: int):
    """Delete meme."""
    user = await require_admin(request)
    meme = await db.get_meme_by_id(meme_id)
    
    if meme:
        # Delete file
        file_path = UPLOAD_DIR / meme["filename"]
        if file_path.exists():
            file_path.unlink()
        
        await db.delete_meme(meme_id)
    
    return {"success": True}


@app.post("/api/meme/{meme_id}/like")
async def api_toggle_like(request: Request, meme_id: int):
    """Toggle like."""
    user = await require_auth(request)
    liked = await db.toggle_like(user["id"], meme_id)
    meme = await db.get_meme_by_id(meme_id)
    
    return {"liked": liked, "likes_count": meme["likes_count"]}


@app.post("/api/meme/{meme_id}/share")
async def api_share_meme(request: Request, meme_id: int):
    """Create share link."""
    user = await require_auth(request)
    token = await db.create_share(meme_id, user["id"])
    
    return {"share_url": f"/share/{token}"}


@app.post("/api/admin/meme/{meme_id}/approve")
async def api_admin_approve_meme(request: Request, meme_id: int):
    """Approve meme (admin API)."""
    user = await require_admin(request)
    await db.approve_meme(meme_id, user["id"])
    return {"success": True}


@app.post("/api/admin/meme/{meme_id}/reject")
async def api_admin_reject_meme(request: Request, meme_id: int):
    """Reject meme (admin API)."""
    user = await require_admin(request)
    body = await request.json() if request.headers.get("content-type") == "application/json" else {}
    reason = body.get("reason", "")
    await db.reject_meme(meme_id, user["id"], reason)
    return {"success": True}


@app.delete("/api/admin/meme/{meme_id}")
async def api_admin_delete_meme(request: Request, meme_id: int):
    """Delete meme (admin API)."""
    user = await require_admin(request)
    meme = await db.get_meme_by_id(meme_id)
    
    if meme:
        file_path = UPLOAD_DIR / meme["filename"]
        if file_path.exists():
            file_path.unlink()
        await db.delete_meme(meme_id)
    
    return {"success": True}


@app.delete("/api/admin/category/{category_id}")
async def api_admin_delete_category(request: Request, category_id: int):
    """Delete category (admin API)."""
    user = await require_admin(request)
    await db.delete_category(category_id)
    return {"success": True}


@app.post("/api/admin/bulk/approve")
async def api_admin_bulk_approve(request: Request):
    """Bulk approve memes."""
    user = await require_admin(request)
    body = await request.json()
    meme_ids = body.get("ids", [])
    await db.bulk_approve(meme_ids, user["id"])
    return {"success": True, "count": len(meme_ids)}


@app.post("/api/admin/bulk/reject")
async def api_admin_bulk_reject(request: Request):
    """Bulk reject memes."""
    user = await require_admin(request)
    body = await request.json()
    meme_ids = body.get("ids", [])
    reason = body.get("reason", "")
    await db.bulk_reject(meme_ids, user["id"], reason)
    return {"success": True, "count": len(meme_ids)}


@app.post("/api/admin/bulk/delete")
async def api_admin_bulk_delete(request: Request):
    """Bulk delete memes."""
    user = await require_admin(request)
    body = await request.json()
    meme_ids = body.get("ids", [])
    
    for meme_id in meme_ids:
        meme = await db.get_meme_by_id(meme_id)
        if meme:
            file_path = UPLOAD_DIR / meme["filename"]
            if file_path.exists():
                file_path.unlink()
    
    await db.bulk_delete(meme_ids)
    return {"success": True, "count": len(meme_ids)}


@app.post("/api/bulk/approve")
async def api_bulk_approve(request: Request, meme_ids: list[int] = Form(...)):
    """Bulk approve memes."""
    user = await require_admin(request)
    await db.bulk_approve(meme_ids, user["id"])
    return {"success": True, "count": len(meme_ids)}


@app.post("/api/bulk/reject")
async def api_bulk_reject(request: Request, meme_ids: list[int] = Form(...), reason: str = Form(None)):
    """Bulk reject memes."""
    user = await require_admin(request)
    await db.bulk_reject(meme_ids, user["id"], reason)
    return {"success": True, "count": len(meme_ids)}


@app.post("/api/bulk/delete")
async def api_bulk_delete(request: Request, meme_ids: list[int] = Form(...)):
    """Bulk delete memes."""
    user = await require_admin(request)
    
    for meme_id in meme_ids:
        meme = await db.get_meme_by_id(meme_id)
        if meme:
            file_path = UPLOAD_DIR / meme["filename"]
            if file_path.exists():
                file_path.unlink()
    
    await db.bulk_delete(meme_ids)
    return {"success": True, "count": len(meme_ids)}


@app.get("/api/stats")
async def api_stats(request: Request):
    """Get statistics."""
    user = await require_admin(request)
    return await db.get_stats()


@app.get("/api/memes")
async def api_get_memes(
    status: str = None,
    category: int = None,
    search: str = None,
    sort: str = "created_at",
    order: str = "desc",
    limit: int = 24,
    offset: int = 0
):
    """Public API to get memes."""
    if status != "approved":
        status = "approved"  # Public API only shows approved
    
    memes = await db.get_memes(
        status=status,
        category_id=category,
        search=search,
        sort_by=sort,
        sort_order=order,
        limit=min(limit, 100),
        offset=offset
    )
    
    return {"memes": memes}


@app.get("/api/categories")
async def api_get_categories():
    """Get all categories."""
    return {"categories": await db.get_categories()}


# Run with: uvicorn web_app:app --host 0.0.0.0 --port 8000 --reload
