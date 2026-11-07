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



# --- F. Reporte de activos (proyección) -------------------------------------
@router.get("/reporte/activos", response_model=List[PersonaActivaRead])
def reporte_activos(db: Session = Depends(get_db)):
    """Solo activos, mostrando únicamente id, email, phone, is_active."""
    return busqueda_service.reporte_activos(db)



# --- H. Desactivación masiva ------------------------------------------------
@router.patch("/bulk/desactivar")
def desactivar_bulk(body: BulkDesactivarRequest, db: Session = Depends(get_db)):
    """Pone is_active = false a una lista de IDs (máximo 100)."""
    return busqueda_service.desactivar_bulk(db, body.ids)