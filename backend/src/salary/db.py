import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass, Session, sessionmaker


class Base(MappedAsDataclass, DeclarativeBase, kw_only=True):
    """Declarative base with dataclass-style construction.

    `MappedAsDataclass` makes Python-level defaults (e.g. `status="active"`)
    apply at object construction, not only at INSERT. `kw_only=True` keeps
    call sites explicit (`Employee(first_name=..., last_name=...)`) and
    sidesteps positional-argument ordering between mixin and subclass.
    """


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

_engine_kwargs: dict = {"future": True}
if DATABASE_URL.startswith("sqlite"):
    # FastAPI uses a thread pool; SQLite needs this to share connections across threads.
    _engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **_engine_kwargs)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, future=True)


def get_session() -> Generator[Session, None, None]:
    """FastAPI dependency. One session per request, committed on success,
    rolled back on any exception escaping the handler."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
