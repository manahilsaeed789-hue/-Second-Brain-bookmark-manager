"""Dashboard and analytics API routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.auth import get_current_user
from backend.database import get_db
from backend.models import User
from backend.schemas import AnalyticsResponse, DashboardStats
from backend.services import bookmark_service, clustering_service

router = APIRouter(prefix="/api", tags=["Dashboard"])


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    stats = bookmark_service.get_dashboard_stats(db, user.id)
    return DashboardStats(**stats)


@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = bookmark_service.get_analytics(db, user.id)
    return AnalyticsResponse(**data)


@router.get("/collections")
async def get_collections(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return bookmark_service.get_collections(db, user.id)


@router.get("/clusters")
async def get_clusters(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return clustering_service.get_semantic_clusters(db, user.id)
