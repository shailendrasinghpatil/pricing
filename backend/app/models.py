from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    oidc_sub = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String)

    watchlist = relationship(
        "WatchlistItem", back_populates="user", cascade="all, delete-orphan"
    )


class WatchlistItem(Base):
    __tablename__ = "watchlist_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    symbol = Column(String, index=True)

    user = relationship("User", back_populates="watchlist")

    __table_args__ = (UniqueConstraint("user_id", "symbol", name="uq_user_symbol"),)
