from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from sqlalchemy import func, text
from ..database import SessionLocal
from ..models import Todos, Users
from .auth import get_current_user
import json
router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)

templates = Jinja2Templates(directory="TodoApp/templates")


# ---------- DB DEPENDENCY ----------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------- HELPERS ----------
def redirect_to_login():
    response = RedirectResponse("/auth/login-page", status_code=302)
    response.delete_cookie("access_token")
    return response


# ---------- ADMIN PAGE (HTML) ----------
@router.get("/dashboard", status_code=status.HTTP_200_OK)
async def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    try:
        user = await get_current_user(request.cookies.get("access_token"))

        if not user or not user.get("is_admin"):
            return redirect_to_login()

        todos = db.query(Todos).all()

        return templates.TemplateResponse(
            "admin-dashboard.html",
            {
                "request": request,
                "todos": todos,
                "user": user,
            },
        )

    except Exception:
        return redirect_to_login()


# ---------- ADMIN API (JSON) ----------
@router.get("/users", status_code=status.HTTP_200_OK)
async def admin_users_page(request: Request, db: Session = Depends(get_db)):
    try:
        user = await get_current_user(request.cookies.get("access_token"))

        if not user or not user.get("is_admin"):
            return redirect_to_login()

        users = db.query(Users).order_by(Users.id).all()

        return templates.TemplateResponse(
            "admin-users.html",
            {
                "request": request,
                "users": users,
                "user": user,
            },
        )

    except Exception:
        return redirect_to_login()


@router.get("/all-todos", status_code=status.HTTP_200_OK)
async def admin_all_todos_page(
    request: Request,
    db: Session = Depends(get_db),
):
    try:
        user = await get_current_user(request.cookies.get("access_token"))

        if not user or not user.get("is_admin"):
            return redirect_to_login()

        todos = db.query(Todos).all()

        return templates.TemplateResponse(
            "admin-all-todos.html",
            {
                "request": request,
                "todos": todos,
                "user": user,
            },
        )

    except Exception:
        return redirect_to_login()


@router.get("/stats", status_code=status.HTTP_200_OK)
async def admin_stats_page(
    request: Request,
    db: Session = Depends(get_db),
):
    try:
        user = await get_current_user(request.cookies.get("access_token"))

        if not user or not user.get("is_admin"):
            return redirect_to_login()

        # ---------- BASIC STATS ----------
        total_users = db.query(Users).count()
        total_todos = db.query(Todos).count()

        completed_todos = (
            db.query(Todos)
            .filter(Todos.complete == True)
            .count()
        )

        open_todos = total_todos - completed_todos

        # ---------- AVG TODOS PER USER ----------
        todos_per_user_subq = (
            db.query(
                Todos.owner_id.label("owner_id"),
                func.count(Todos.id).label("todo_count"),
            )
            .group_by(Todos.owner_id)
            .subquery()
        )

        avg_todos_per_user = db.query(
            func.avg(todos_per_user_subq.c.todo_count)
        ).scalar()

        completion_rate = (
            round((completed_todos / total_todos) * 100, 1)
            if total_todos > 0 else 0
        )

        # ---------- TOP USERS ----------
        top_users = (
            db.query(
                Users.username,
                func.count(Todos.id).label("todo_count")
            )
            .join(Todos, Todos.owner_id == Users.id)
            .group_by(Users.username)
            .order_by(func.count(Todos.id).desc())
            .limit(5)
            .all()
        )

        most_productive_user = (
            db.query(
                Users.username,
                func.count(Todos.id).label("todo_count"),
            )
            .join(Todos, Todos.owner_id == Users.id)
            .group_by(Users.username)
            .order_by(func.count(Todos.id).desc())
            .first()
        )

        top_usernames = [u.username for u in top_users]
        top_counts = [u.todo_count for u in top_users]

        # ---------- DEAD ACCOUNTS ----------
        dead_accounts_count = (
            db.query(Users)
            .outerjoin(Todos, Todos.owner_id == Users.id)
            .group_by(Users.id)
            .having(func.count(Todos.id) == 0)
            .count()
        )

        # ---------- TODOS CREATED PER DAY (LAST 14 DAYS) ----------
        daily_created = (
            db.query(
                func.date_trunc("day", Todos.created_at).label("day"),
                func.count(Todos.id).label("count"),
            )
            .filter(Todos.created_at >= (func.now() - text("interval '14 days'")))
            .group_by("day")
            .order_by("day")
            .all()
        )

        daily_labels = [d.day.strftime("%Y-%m-%d") for d in daily_created]
        daily_counts = [d.count for d in daily_created]

        # ---------- RENDER ----------
        return templates.TemplateResponse(
            "admin-stats.html",
            {
                "request": request,
                "user": user,
                "total_users": total_users,
                "total_todos": total_todos,
                "completed_todos": completed_todos,
                "open_todos": open_todos,
                "avg_todos_per_user": round(avg_todos_per_user or 0, 2),
                "completion_rate": completion_rate,
                "top_users": top_users,
                "top_usernames": json.dumps(top_usernames),
                "top_counts": json.dumps(top_counts),
                "most_productive_user": most_productive_user,
                "dead_accounts_count": dead_accounts_count,
                "daily_labels": json.dumps(daily_labels),
                "daily_counts": json.dumps(daily_counts),

            },
        )

    except Exception:
        return redirect_to_login()
