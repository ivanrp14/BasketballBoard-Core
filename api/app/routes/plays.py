from app.schemas.play import PlayCreateRequest
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from bson import ObjectId
from typing import List

from app import models, db
from app.core import get_current_user
import json
from app.db.mongo import get_mongo_client

router = APIRouter(prefix="/plays")

def get_plays_collection():
    mongo_db = get_mongo_client()
    return mongo_db["plays_data"]

# 🔹 Middleware/función de permisos
async def check_user_role(user: models.User, team_id: int, db_sess: AsyncSession, allowed_roles: List[str]):
    result = await db_sess.execute(
        select(models.Permission).filter_by(user_id=user.id, team_id=team_id)
    )
    perm = result.scalar_one_or_none()
    if not perm or perm.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos suficientes para esta acción"
        )
    return perm

# 📌 Crear jugada
@router.post("/", status_code=201)
async def create_play(
    request: PlayCreateRequest,
    current_user: models.User = Depends(get_current_user),
    db_sess: AsyncSession = Depends(db.get_db)
):
    await check_user_role(current_user, request.team_id, db_sess, ["admin", "editor"])

    new_play = models.Play(team_id=request.team_id, name=request.name)
    db_sess.add(new_play)
    await db_sess.commit()
    await db_sess.refresh(new_play)

    plays_collection = get_plays_collection()
    try:
        data_dict = json.loads(request.data)  # convertir string JSON a dict
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"JSON inválido: {e}")

    await plays_collection.insert_one({
        "play_id": new_play.id,
        "data": data_dict  # ahora se guarda como objeto
    })

    return {
        "id": new_play.id,
        "team_id": request.team_id,
        "name": request.name,
        "created_at": new_play.created_at
    }

# 📌 Actualizar jugada
@router.put("/{play_id}")
async def update_play(
    play_id: int,
    name: str = None,
    data: str = None,  # string JSON desde Unity
    current_user: models.User = Depends(get_current_user),
    db_sess: AsyncSession = Depends(db.get_db)
):
    result = await db_sess.execute(select(models.Play).filter_by(id=play_id))
    play = result.scalar_one_or_none()
    if not play:
        raise HTTPException(status_code=404, detail="Jugada no encontrada")

    await check_user_role(current_user, play.team_id, db_sess, ["admin", "editor"])

    if name:
        play.name = name
    db_sess.add(play)
    await db_sess.commit()

    if data:
        try:
            data_dict = json.loads(data)
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"JSON inválido: {e}")

        plays_collection = get_plays_collection()
        await plays_collection.update_one(
            {"play_id": play.id},
            {"$set": {"data": data_dict}},
            upsert=True
        )

    return {"id": play.id, "name": play.name, "team_id": play.team_id}


@router.get("/{team_id}")
async def list_team_play_names(
    team_id: int,
    current_user: models.User = Depends(get_current_user),
    db_sess: AsyncSession = Depends(db.get_db)
):
    # validar que el usuario es parte del equipo
    await check_user_role(current_user, team_id, db_sess, ["admin", "editor", "viewer"])

    result = await db_sess.execute(select(models.Play).filter_by(team_id=team_id))
    plays = result.scalars().all()

    return [{"id": play.id, "name": play.name, "created_at": play.created_at} for play in plays]
@router.get("/{play_id}/data")
async def get_play_data(
    play_id: int,
    current_user: models.User = Depends(get_current_user),
    db_sess: AsyncSession = Depends(db.get_db)
):
    result = await db_sess.execute(select(models.Play).filter_by(id=play_id))
    play = result.scalar_one_or_none()
    if not play:
        raise HTTPException(status_code=404, detail="Jugada no encontrada")

    await check_user_role(current_user, play.team_id, db_sess, ["admin", "editor", "viewer"])

    plays_collection = get_plays_collection()
    mongo_doc = await plays_collection.find_one({"play_id": play.id})

    data_obj = mongo_doc["data"] if mongo_doc else None

    # 🔥 Aquí el fix: devolver JSON real, no string
    return {
        "id": play.id,
        "name": play.name,
        "team_id": play.team_id,
        "created_at": play.created_at,
        "data": data_obj
    }


# 📌 Eliminar jugada
@router.delete("/{play_id}", status_code=204)
async def delete_play(
    play_id: int,
    current_user: models.User = Depends(get_current_user),
    db_sess: AsyncSession = Depends(db.get_db)
):
    result = await db_sess.execute(select(models.Play).filter_by(id=play_id))
    play = result.scalar_one_or_none()
    if not play:
        raise HTTPException(status_code=404, detail="Jugada no encontrada")

    # validar rol
    await check_user_role(current_user, play.team_id, db_sess, ["admin", "editor"])

    # eliminar en Postgres
    await db_sess.delete(play)
    await db_sess.commit()

    # eliminar en Mongo
    plays_collection = get_plays_collection()
    await plays_collection.delete_one({"play_id": play.id})

    return {"detail": "Jugada eliminada"}
@router.get("/{team_id}/full")
async def get_full_team_plays(
    team_id: int,
    current_user: models.User = Depends(get_current_user),
    db_sess: AsyncSession = Depends(db.get_db)
):
    # validar permisos
    await check_user_role(current_user, team_id, db_sess, ["admin", "editor", "viewer"])

    # obtener jugadas desde Postgres
    result = await db_sess.execute(select(models.Play).filter_by(team_id=team_id))
    plays = result.scalars().all()

    if not plays:
        return []

    # obtener coleccion mongo
    plays_collection = get_plays_collection()

    # obtener todos los play_id
    play_ids = [p.id for p in plays]

    # traer documentos desde mongo
    mongo_docs = await plays_collection.find({"play_id": {"$in": play_ids}}).to_list(length=None)

    # convertir a diccionario por play_id
    mongo_map = {doc["play_id"]: doc.get("data") for doc in mongo_docs}

    # unir datos
    full_plays = []
    for p in plays:
        full_plays.append({
            "id": p.id,
            "team_id": p.team_id,
            "name": p.name,
            "created_at": p.created_at,
            "data": mongo_map.get(p.id)  # None si no existe en mongo
        })

    return full_plays
