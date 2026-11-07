from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..views.persona import PersonaRead
from ..views.busqueda import PersonaActivaRead, BulkDesactivarRequest
from ..services import busqueda_service

router = APIRouter(prefix="/personas", tags=["busqueda y bulk"])


# --- E. Buscador general ----------------------------------------------------
@router.get("/buscar/{termino}", response_model=List[PersonaRead])
def buscar_personas(termino: str, db: Session = Depends(get_db)):
    """Busca en first_name, last_name o email. Si no hay nada, devuelve []."""
    return busqueda_service.buscar_personas(db, termino)