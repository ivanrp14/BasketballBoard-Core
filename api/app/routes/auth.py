# auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete, or_
from app import db, models, schemas
from app.core.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user
)

router = APIRouter(prefix="/auth", tags=["Auth"])


# 👉 Registro de usuario
@router.post("/register", response_model=schemas.UserOut)
async def register(user: schemas.UserCreate, db_sess: AsyncSession = Depends(db.get_db)):
    # Verificar si ya existe por email
    result = await db_sess.execute(select(models.User).filter(models.User.email == user.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Verificar si ya existe por username
    if user.username:
        result = await db_sess.execute(select(models.User).filter(models.User.username == user.username))
        existing_username = result.scalar_one_or_none()
        if existing_username:
            raise HTTPException(status_code=400, detail="Username already taken")

    new_user = models.User(
        email=user.email,
        username=user.username,
        password_hash=get_password_hash(user.password),
    )
    db_sess.add(new_user)
    await db_sess.commit()
    await db_sess.refresh(new_user)
    return new_user



@router.post("/login", response_model=schemas.Token)
async def login(form_data: schemas.UserLogin, db_sess: AsyncSession = Depends(db.get_db)):
    result = await db_sess.execute(
        select(models.User).filter(
            or_(models.User.username == form_data.username, models.User.email == form_data.username)
        )
    )
    user = result.scalar_one_or_none()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}



# 👉 Info del usuario logueado
@router.get("/me", response_model=schemas.UserOut)
async def me(current_user: models.User = Depends(get_current_user)):
    return schemas.UserOut.from_orm(current_user)


# 👉 Borrar todos los usuarios
@router.delete("/delete_all", status_code=204)
async def delete_all_users(
    db_sess: AsyncSession = Depends(db.get_db),
    
):
    await db_sess.execute(delete(models.User))
    await db_sess.commit()
    return None

