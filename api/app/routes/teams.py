import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app import schemas, db
from app.models import Team, Permission, User
from app.routes.auth import get_current_user
from sqlalchemy.orm import aliased

router = APIRouter(prefix="/teams", tags=["Teams"])
@router.post("/", response_model=schemas.TeamOut)
async def create_team(
    team: schemas.TeamCreate,
    db_sess: AsyncSession = Depends(db.get_db),
    current_user: User = Depends(get_current_user)
):
    # Obtener todos los equipos donde el usuario es admin
    result = await db_sess.execute(
        select(Permission).filter(Permission.user_id == current_user.id, Permission.role == "admin")
    )
    existing_permissions = result.scalars().all()

    # Limite de 3 equipos por usuario
    if len(existing_permissions) >= 10:
        raise HTTPException(status_code=409, detail="You already own 10 teams")

    # Validar que no exista un equipo con el mismo nombre para este usuario
    for perm in existing_permissions:
        team_result = await db_sess.execute(
            select(Team).filter(Team.id == perm.team_id, Team.name == team.name.upper())
        )
        existing_team_same_name = team_result.scalar_one_or_none()
        if existing_team_same_name:
            raise HTTPException(status_code=409, detail="You already have a team with this name")

    # Crear nuevo equipo
    new_team = Team(
        name=team.name.upper(),
        color=team.color,
        invitation_code=str(uuid.uuid4())[:8]
    )
    db_sess.add(new_team)
    await db_sess.commit()
    await db_sess.refresh(new_team)

    # Crear permiso admin para el creador
    perm = Permission(user_id=current_user.id, team_id=new_team.id, role="admin")
    db_sess.add(perm)
    await db_sess.commit()

    return schemas.TeamOut.from_orm(new_team)



# 📌 Listar todos los equipos
@router.get("/", response_model=list[schemas.TeamOut])
async def list_teams(db_sess: AsyncSession = Depends(db.get_db)):
    result = await db_sess.execute(select(Team))
    teams = result.scalars().all()
    return [schemas.TeamOut.from_orm(t) for t in teams]

@router.get("/me", response_model=list[schemas.PermissionOut])
async def get_my_team(
    db_sess: AsyncSession = Depends(db.get_db),
    current_user: User = Depends(get_current_user)
):
    # Alias para encontrar al owner
    owner_perm = aliased(Permission)
    owner_user = aliased(User)

    result = await db_sess.execute(
        select(Permission, Team, owner_user.username)
        .join(Team, Permission.team_id == Team.id)
        .join(owner_perm, owner_perm.team_id == Team.id)
        .join(owner_user, owner_user.id == owner_perm.user_id)
        .filter(Permission.user_id == current_user.id)
        
    )
    permissions = result.all()

    return [
        schemas.PermissionOut(
            id=perm.Permission.id,
            username=current_user.username,
            team_name=perm.Team.name,
            team_color=perm.Team.color,
            team_id=perm.Team.id,
            role=perm.Permission.role,
            owner=perm.username  # username del admin
        )
        for perm in permissions
    ]

# 📌 Unirse a un equipo con invitation_code
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
        raise HTTPException(status_code=400, detail="Not valid or used")

    # Verificar si ya es miembro
    result = await db_sess.execute(
        select(Permission).filter(
            Permission.user_id == current_user.id,
            Permission.team_id == team.id
        )
    )
    existing_permission = result.scalar_one_or_none()
    if existing_permission:
        raise HTTPException(status_code=400, detail="Not valid or used")

    # Agregar como viewer
    new_permission = Permission(user_id=current_user.id, team_id=team.id, role="viewer")
    db_sess.add(new_permission)

    # Invalidar código usado
    team.invitation_code = str(uuid.uuid4())[:8]
    db_sess.add(team)

    await db_sess.commit()
    await db_sess.refresh(team)

    return schemas.TeamOut.from_orm(team)


# 📌 Salir de un equipo
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

    # El dueño/admin no puede salirse
    if permission.role == "admin":
        raise HTTPException(status_code=400, detail="Admin cannot leave their own team")

    await db_sess.delete(permission)
    await db_sess.commit()
    return None


# 📌 Eliminar equipo (solo admin)
@router.delete("/{team_id}", status_code=204)
async def delete_team(
    team_id: int,
    db_sess: AsyncSession = Depends(db.get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db_sess.execute(
        select(Permission).filter(
            Permission.team_id == team_id,
            Permission.user_id == current_user.id,
            Permission.role == "admin"
        )
    )
    admin_perm = result.scalar_one_or_none()
    if not admin_perm:
        raise HTTPException(status_code=404, detail="Team not found or you are not admin")

    # Borrar el equipo
    result = await db_sess.execute(select(Team).filter(Team.id == team_id))
    team = result.scalar_one_or_none()
    if team:
        await db_sess.delete(team)
        await db_sess.commit()

    return None


# 📌 Miembros de un equipo
@router.get("/{team_id}/members", response_model=list[schemas.PermissionOut])
async def get_team_members(team_id: int, db_sess: AsyncSession = Depends(db.get_db)):
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


# 📌 Obtener invitation_code (solo admin)
@router.get("/{team_id}/invitation-code")
async def get_invitation_code(
    team_id: int,
    db_sess: AsyncSession = Depends(db.get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db_sess.execute(
        select(Permission).filter(
            Permission.team_id == team_id,
            Permission.user_id == current_user.id,
            Permission.role == "admin"
        )
    )
    admin_perm = result.scalar_one_or_none()
    if not admin_perm:
        raise HTTPException(status_code=404, detail="Team not found or you are not admin")

    result = await db_sess.execute(select(Team).filter(Team.id == team_id))
    team = result.scalar_one_or_none()
    return {"team_id": team.id, "invitation_code": team.invitation_code}


# 📌 Obtener invitation_url (solo admin)
@router.get("/{team_id}/invitation-url")
async def get_invitation_url(
    team_id: int,
    request: Request,
    db_sess: AsyncSession = Depends(db.get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db_sess.execute(
        select(Permission).filter(
            Permission.team_id == team_id,
            Permission.user_id == current_user.id,
            Permission.role == "admin"
        )
    )
    admin_perm = result.scalar_one_or_none()
    if not admin_perm:
        raise HTTPException(status_code=404, detail="Team not found or you are not admin")

    result = await db_sess.execute(select(Team).filter(Team.id == team_id))
    team = result.scalar_one_or_none()

    base_url = str(request.base_url).rstrip("/")
    invitation_url = f"{base_url}/teams/join/{team.invitation_code}"

    return {"team_id": team.id, "invitation_url": invitation_url}
