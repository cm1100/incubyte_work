from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass


class Base(MappedAsDataclass, DeclarativeBase, kw_only=True):
    """Declarative base with dataclass-style construction.

    `MappedAsDataclass` makes Python-level defaults (e.g. `status="active"`)
    apply at object construction, not only at INSERT. `kw_only=True` keeps
    call sites explicit (`Employee(first_name=..., last_name=...)`) and
    sidesteps positional-argument ordering between mixin and subclass.
    """
