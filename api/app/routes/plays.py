from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, db
from app.routes.auth import get_current_user

router = APIRouter(prefix="/plays", tags=["Plays"])

@router.post("/{team_id}", response_model=schemas.PlayOut)
def create_play(team_id: int, play: schemas.PlayCreate, db_sess: Session = Depends(db.get_db), current_user: models.User = Depends(get_current_user)):
    # check permissions
    perm = db_sess.query(models.Permission).filter_by(user_id=current_user.id, team_id=team_id).first()
    if not perm or perm.role not in ["admin", "editor"]:
        raise HTTPException(status_code=403, detail="Not allowed")

    # limit 30 plays
    count = db_sess.query(models.Play).filter(models.Play.team_id == team_id).count()
    if count >= 30:
        raise HTTPException(status_code=400, detail="Team already has max 30 plays")

    new_play = models.Play(team_id=team_id, name=play.name)
    db_sess.add(new_play)
    db_sess.commit()
    db_sess.refresh(new_play)
    return new_play

@router.get("/{team_id}", response_model=list[schemas.PlayOut])
def list_plays(team_id: int, db_sess: Session = Depends(db.get_db), current_user: models.User = Depends(get_current_user)):
    perm = db_sess.query(models.Permission).filter_by(user_id=current_user.id, team_id=team_id).first()
    if not perm:
        raise HTTPException(status_code=403, detail="Not allowed")
    return db_sess.query(models.Play).filter_by(team_id=team_id).all()
