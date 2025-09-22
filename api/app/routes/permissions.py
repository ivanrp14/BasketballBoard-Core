from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, db
from app.auth.oauth2 import get_current_user

router = APIRouter(prefix="/permissions", tags=["Permissions"])

@router.post("/{team_id}", response_model=schemas.PermissionOut)
def add_permission(team_id: int, perm: schemas.PermissionCreate, db_sess: Session = Depends(db.get_db), current_user: models.User = Depends(get_current_user)):
    # only admin can manage permissions
    admin_perm = db_sess.query(models.Permission).filter_by(user_id=current_user.id, team_id=team_id, role="admin").first()
    if not admin_perm:
        raise HTTPException(status_code=403, detail="Not allowed")

    new_perm = models.Permission(user_id=perm.user_id, team_id=team_id, role=perm.role)
    db_sess.add(new_perm)
    db_sess.commit()
    db_sess.refresh(new_perm)
    return new_perm

@router.get("/{team_id}", response_model=list[schemas.PermissionOut])
def list_permissions(team_id: int, db_sess: Session = Depends(db.get_db), current_user: models.User = Depends(get_current_user)):
    admin_perm = db_sess.query(models.Permission).filter_by(user_id=current_user.id, team_id=team_id, role="admin").first()
    if not admin_perm:
        raise HTTPException(status_code=403, detail="Not allowed")

    return db_sess.query(models.Permission).filter_by(team_id=team_id).all()
