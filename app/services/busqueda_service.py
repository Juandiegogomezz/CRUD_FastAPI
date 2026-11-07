from typing import Sequence
from sqlalchemy.orm import Session

from ..models.persona import Persona


# --- E. GET /personas/buscar/{termino} ------------------------------------
def buscar_personas(db: Session, termino: str) -> Sequence[Persona]:
    """Busca el término en first_name O last_name O email."""
    patron = f"%{termino}%"
    return (
        db.query(Persona)
        .filter(
            (Persona.first_name.like(patron))
            | (Persona.last_name.like(patron))
            | (Persona.email.like(patron))
        )
        .all()
    )