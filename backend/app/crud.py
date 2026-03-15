from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app import models, schemas


def get_user_by_sub(db: Session, oidc_sub: str) -> models.User | None:
    return db.query(models.User).filter(models.User.oidc_sub == oidc_sub).first()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    db_user = models.User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_or_create_user(
    db: Session, oidc_sub: str, email: str, username: str
) -> models.User:
    user = get_user_by_sub(db, oidc_sub)
    if not user:
        user = create_user(
            db,
            schemas.UserCreate(oidc_sub=oidc_sub, email=email, username=username),
        )
    return user


def get_watchlist(db: Session, user_id: int) -> list[models.WatchlistItem]:
    return (
        db.query(models.WatchlistItem)
        .filter(models.WatchlistItem.user_id == user_id)
        .all()
    )


def add_to_watchlist(
    db: Session, user_id: int, symbol: str
) -> models.WatchlistItem | None:
    item = models.WatchlistItem(user_id=user_id, symbol=symbol.upper())
    db.add(item)
    try:
        db.commit()
        db.refresh(item)
        return item
    except IntegrityError:
        db.rollback()
        return None


def remove_from_watchlist(db: Session, user_id: int, symbol: str) -> None:
    db.query(models.WatchlistItem).filter(
        models.WatchlistItem.user_id == user_id,
        models.WatchlistItem.symbol == symbol.upper(),
    ).delete()
    db.commit()
