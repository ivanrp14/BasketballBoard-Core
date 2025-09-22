import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app import models, schemas, db
from app.routes.auth import get_current_user
router = APIRouter(prefix="/teams", tags=["Teams"])

@router.post("/", response_model=schemas.TeamOut)
async def create_team(
    team: schemas.TeamCreate,
    db_sess: AsyncSession = Depends(db.get_db),
    current_user: models.User = Depends(get_current_user)
):
    # un usuario solo puede tener 1 equipo
    result = await db_sess.execute(
        select(models.Team).filter(models.Team.owner_id == current_user.id)
    )
    existing_team = result.scalar_one_or_none()

    if existing_team:
        raise HTTPException(status_code=400, detail="User already owns a team")

    new_team = models.Team(
        name=team.name,
        color=team.color,
        invitation_code=str(uuid.uuid4())[:8],
        owner_id=current_user.id
    )
    db_sess.add(new_team)
    await db_sess.commit()
    await db_sess.refresh(new_team)

    # el creador tiene rol admin
    perm = models.Permission(user_id=current_user.id, team_id=new_team.id, role="admin")
    db_sess.add(perm)
    await db_sess.commit()

    return new_team

@router.get("/", response_model=list[schemas.TeamOut])
async def list_teams(
    db_sess: AsyncSession = Depends(db.get_db),
    current_user: models.User = Depends(get_current_user)
):
    result = await db_sess.execute(
        select(models.Team)
        .join(models.Permission)
        .filter(models.Permission.user_id == current_user.id)
    )
    teams = result.scalars().all()
    return teams
