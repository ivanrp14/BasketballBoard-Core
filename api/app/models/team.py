from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import relationship
from app.db import Base





class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    color = Column(String, nullable=False)
    invitation_code = Column(String, unique=True, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), unique=True)

    # Relaciones
    owner = relationship("User", back_populates="team")
    plays = relationship("Play", back_populates="team")
    permissions = relationship("Permission", back_populates="team")
