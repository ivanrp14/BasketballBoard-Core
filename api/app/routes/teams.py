import uuid
from app import models
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app import schemas, db
from app.models import Team, Permission, User
from app.routes.auth import get_current_user
router = APIRouter(prefix="/teams", tags=["Teams"])

@router.post("/", response_model=schemas.TeamOut)
async def create_team(
    team: schemas.TeamCreate,
    db_sess: AsyncSession = Depends(db.get_db),
    current_user: User = Depends(get_current_user)
):
    # un usuario solo puede tener 1 equipo
    result = await db_sess.execute(
        select(Team).filter(    Team.owner_id == current_user.id)
    )
    existing_team = result.scalar_one_or_none()

    if existing_team:
        raise HTTPException(status_code=400, detail="User already owns a team")

    new_team = Team(
        name=team.name,
        color=team.color,
        invitation_code=str(uuid.uuid4())[:8],
        owner_id=current_user.id
    )
    db_sess.add(new_team)
    await db_sess.commit()
    await db_sess.refresh(new_team)

    # el creador tiene rol admin
    perm = Permission(user_id=current_user.id, team_id=new_team.id, role="admin")
    db_sess.add(perm)
    await db_sess.commit()

    return new_team

@router.get("/", response_model=list[schemas.TeamOut])
async def list_teams(
    db_sess: AsyncSession = Depends(db.get_db),
    
):
    result = await db_sess.execute(
        select(Team)
        
    )
    teams = result.scalars().all()
    return teams


@router.get("/me", response_model=list[schemas.PermissionOut])
async def get_my_team(

    db: AsyncSession = Depends(db.get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Permission, Team)
        .join(Team, Permission.team_id == Team.id)
        .filter(Permission.user_id == current_user.id)
    )
    permissions = result.all()

    permissions_out = [
        schemas.PermissionOut(
            id=perm.Permission.id,
            team_name=perm.Team.name,
            team_color=perm.Team.color,
            role=perm.Permission.role
        )
        for perm in permissions
    ]

    return permissions_out
    
@router.post("/join/{invitation_code}", response_model=schemas.TeamOut)
async def join_team(
    invitation_code: str,
    db_sess: AsyncSession = Depends(db.get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db_sess.execute(
        select(Team).filter(Team.invitation_code == invitation_code)
    )
    team = result.scalar_one_or_none()

    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    # Check if the user is already a member of the team
    result = await db_sess.execute(
        select(Permission).filter(
            Permission.user_id == current_user.id,
            Permission.team_id == team.id
        )
    )
    existing_permission = result.scalar_one_or_none()

    if existing_permission:
        raise HTTPException(status_code=400, detail="User is already a member of the team")

    # Add the user to the team with a default role
    new_permission = Permission(
        user_id=current_user.id,
        team_id=team.id,
        role="viewer"
    )
    db_sess.add(new_permission)
    await db_sess.commit()

    return team


@router.post("/leave/{team_id}", status_code=204)
async def leave_team(
    team_id: int,
    db_sess: AsyncSession = Depends(db.get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db_sess.execute(
        select(Permission).filter(
            Permission.user_id == current_user.id,
            Permission.team_id == team_id
        )
    )
    permission = result.scalar_one_or_none()

    if not permission:
        raise HTTPException(status_code=404, detail="Membership not found")

    # Prevent the owner from leaving their own team
    result = await db_sess.execute(
        select(Team).filter(
            Team.id == team_id,
            Team.owner_id == current_user.id
        )
    )
    team = result.scalar_one_or_none()

    if team:
        raise HTTPException(status_code=400, detail="Team owner cannot leave their own team")

    await db_sess.delete(permission)
    await db_sess.commit()
    return None

@router.delete("/{team_id}", status_code=204)
async def delete_team(
    team_id: int,
    db_sess: AsyncSession = Depends(db.get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db_sess.execute(
        select(Team).filter(Team.id == team_id, Team.owner_id == current_user.id)
    )
    team = result.scalar_one_or_none()

    if not team:
        raise HTTPException(status_code=404, detail="Team not found or not owned by user")

    await db_sess.delete(team)
    await db_sess.commit()
    return None


@router.get("{team_id}/members", response_model=list[schemas.PermissionOut] )
async def get_team_members(
    team_id: int,
    db_sess: AsyncSession = Depends(db.get_db),
    current_user: User = Depends(get_current_user)
):
    import uuid
from app import models
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app import schemas, db
from app.models import Team, Permission, User
from app.routes.auth import get_current_user
router = APIRouter(prefix="/teams", tags=["Teams"])

@router.post("/", response_model=schemas.TeamOut)
async def create_team(
    team: schemas.TeamCreate,
    db_sess: AsyncSession = Depends(db.get_db),
    current_user: User = Depends(get_current_user)
):
    # un usuario solo puede tener 1 equipo
    result = await db_sess.execute(
        select(Team).filter(    Team.owner_id == current_user.id)
    )
    existing_team = result.scalar_one_or_none()

    if existing_team:
        raise HTTPException(status_code=400, detail="User already owns a team")

    new_team = Team(
        name=team.name,
        color=team.color,
        invitation_code=str(uuid.uuid4())[:8],
        owner_id=current_user.id
    )
    db_sess.add(new_team)
    await db_sess.commit()
    await db_sess.refresh(new_team)

    # el creador tiene rol admin
    perm = Permission(user_id=current_user.id, team_id=new_team.id, role="admin")
    db_sess.add(perm)
    await db_sess.commit()

    return new_team

@router.get("/", response_model=list[schemas.TeamOut])
async def list_teams(
    db_sess: AsyncSession = Depends(db.get_db),
    
):
    result = await db_sess.execute(
        select(Team)
        
    )
    teams = result.scalars().all()
    return teams


@router.get("/me", response_model=list[schemas.PermissionOut])
async def get_my_team(

    db: AsyncSession = Depends(db.get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Permission, Team)
        .join(Team, Permission.team_id == Team.id)
        .filter(Permission.user_id == current_user.id)
    )
    permissions = result.all()

    permissions_out = [
        schemas.PermissionOut(
            id=perm.Permission.id,
            username=current_user.username,
            team_name=perm.Team.name,
            team_color=perm.Team.color,
            role=perm.Permission.role
        )
        for perm in permissions
    ]

    return permissions_out
    
@router.post("/join/{invitation_code}", response_model=schemas.TeamOut)
async def join_team(
    invitation_code: str,
    db_sess: AsyncSession = Depends(db.get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db_sess.execute(
        select(Team).filter(Team.invitation_code == invitation_code)
    )
    team = result.scalar_one_or_none()

    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    # Check if the user is already a member of the team
    result = await db_sess.execute(
        select(Permission).filter(
            Permission.user_id == current_user.id,
            Permission.team_id == team.id
        )
    )
    existing_permission = result.scalar_one_or_none()

    if existing_permission:
        raise HTTPException(status_code=400, detail="User is already a member of the team")

    # Add the user to the team with a default role
    new_permission = Permission(
        user_id=current_user.id,
        team_id=team.id,
        role="viewer"
    )
    db_sess.add(new_permission)
    await db_sess.commit()

    return team


@router.post("/leave/{team_id}", status_code=204)
async def leave_team(
    team_id: int,
    db_sess: AsyncSession = Depends(db.get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db_sess.execute(
        select(Permission).filter(
            Permission.user_id == current_user.id,
            Permission.team_id == team_id
        )
    )
    permission = result.scalar_one_or_none()

    if not permission:
        raise HTTPException(status_code=404, detail="Membership not found")

    # Prevent the owner from leaving their own team
    result = await db_sess.execute(
        select(Team).filter(
            Team.id == team_id,
            Team.owner_id == current_user.id
        )
    )
    team = result.scalar_one_or_none()

    if team:
        raise HTTPException(status_code=400, detail="Team owner cannot leave their own team")

    await db_sess.delete(permission)
    await db_sess.commit()
    return None

@router.delete("/{team_id}", status_code=204)
async def delete_team(
    team_id: int,
    db_sess: AsyncSession = Depends(db.get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db_sess.execute(
        select(Team).filter(Team.id == team_id, Team.owner_id == current_user.id)
    )
    team = result.scalar_one_or_none()

    if not team:
        raise HTTPException(status_code=404, detail="Team not found or not owned by user")

    await db_sess.delete(team)
    await db_sess.commit()
    return None

@router.get("/{team_id}/members", response_model=list[schemas.PermissionOut])
async def get_team_members(
    team_id: int,
    db_sess: AsyncSession = Depends(db.get_db),
):
    result = await db_sess.execute(
        select(Permission.id, Permission.role, Team.name, Team.color, User.username)
        .join(Team, Permission.team_id == Team.id)
        .join(User, Permission.user_id == User.id)
        .filter(Permission.team_id == team_id)
    )
    rows = result.all()

    return [
        schemas.PermissionOut(
            id=row.id,
            username=row.username,
            team_name=row.name,
            team_color=row.color,
            role=row.role
        )
        for row in rows
    ]
