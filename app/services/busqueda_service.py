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



# --- F. GET /personas/reporte/activos -------------------------------------
def reporte_activos(db: Session) -> Sequence[Persona]:
    """Solo las personas con is_active = true."""
    return db.query(Persona).filter(Persona.is_active.is_(True)).all()



# --- H. PATCH /personas/bulk/desactivar -----------------------------------
def desactivar_bulk(db: Session, ids: list[int]) -> dict:
    """Pone is_active = false a los IDs que existan; reporta los que no."""
    ids_unicos = list(dict.fromkeys(ids))  # quita repetidos, conserva el orden

    existentes = {
        fila[0] for fila in db.query(Persona.id).filter(Persona.id.in_(ids_unicos)).all()
    }
    desactivados = [i for i in ids_unicos if i in existentes]
    no_encontrados = [i for i in ids_unicos if i not in existentes]

    if desactivados:
        # Un solo UPDATE ... WHERE id IN (...) — una sola operación
        db.query(Persona).filter(Persona.id.in_(desactivados)).update(
            {Persona.is_active: False}, synchronize_session=False
        )
        db.commit()

    return {
        "message": "Operación completada.",
        "desactivados": desactivados,
        "no_encontrados": no_encontrados,
        "total_desactivados": len(desactivados),
    }