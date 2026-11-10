from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from ..views.persona import PersonaCreate, PersonaUpdate, PersonaRead, PoblarRequest
from fastapi.responses import StreamingResponse

from ..database import get_db
from ..views.persona import PersonaCreate, PersonaUpdate, PersonaRead
from ..services import persona_service
from ..views.persona import EdadEstadisticas

router = APIRouter(prefix="/personas", tags=["personas"])


@router.post("", response_model=PersonaRead, status_code=status.HTTP_201_CREATED)
def create_persona(persona_in: PersonaCreate, db: Session = Depends(get_db)):
    """Create a new Persona delegating to service layer."""
    # Let domain errors bubble up to global handlers
    return persona_service.create_persona(db, persona_in)


@router.get("", response_model=List[PersonaRead])
def list_personas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """List Personas with pagination via service layer."""
    return persona_service.list_personas(db, skip=skip, limit=limit)


@router.get("/{persona_id}", response_model=PersonaRead)
def get_persona(persona_id: int, db: Session = Depends(get_db)):
    """Retrieve a Persona by ID via service layer."""
    return persona_service.get_persona(db, persona_id)


@router.put("/{persona_id}", response_model=PersonaRead)
def update_persona(persona_id: int, persona_in: PersonaUpdate, db: Session = Depends(get_db)):
    """Update an existing Persona (partial) via service layer."""
    return persona_service.update_persona(db, persona_id, persona_in)

# IMPORTANTE: esta ruta debe declararse ANTES que
# @router.delete("/{persona_id}", ...) de mas abajo. Si quedara despues,
# FastAPI interpretaria la palabra "reset" como si fuera un intento de
# persona_id (ya que /{persona_id} acepta cualquier texto), y respondería
# con 422 Unprocessable Entity en vez de ejecutar el reset.
@router.delete("/reset")
def reset_personas(db: Session = Depends(get_db)):
    """Delete all Personas to reset the lab environment."""
    eliminados = persona_service.reset_personas(db)
    return {
        "message": "Base de datos limpiada. Se eliminaron todos los registros.",
        "deleted_count": eliminados,
    }

@router.delete("/{persona_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_persona(persona_id: int, db: Session = Depends(get_db)):
    """Delete a Persona by ID via service layer."""
    persona_service.delete_persona(db, persona_id)
    return None


@router.get("/estadisticas/edad", response_model=EdadEstadisticas)
def get_edad_stats(db: Session = Depends(get_db)):
    """Return average, min and max age of Personas via service layer."""
    return persona_service.get_edad_stats(db)
@router.post("/poblar", status_code=status.HTTP_201_CREATED)
def poblar_personas(payload: PoblarRequest, db: Session = Depends(get_db)):
    """Bulk-create Personas using Faker-generated data."""
    # La validacion de "cantidad" ya ocurrio automaticamente en el
    # schema PoblarRequest (ver app/views/persona.py), por eso aqui
    # solo delegamos la logica pesada a la capa de servicios
    creados = persona_service.poblar_personas(db, payload.cantidad)
    return {
        "message": f"{creados} usuarios creados exitosamente",
        "status": status.HTTP_201_CREATED,
    }
@router.get("/exportar/csv")
def exportar_csv(db: Session = Depends(get_db)):
    """Export all Personas as a downloadable CSV file."""
    buffer = persona_service.exportar_personas_csv(db)
    # StreamingResponse envia el contenido progresivamente en vez de
    # cargarlo todo de una vez en memoria como una respuesta normal,
    # tal como lo sugiere el enunciado del laboratorio
    return StreamingResponse(
        buffer,
        media_type="text/csv",
        # Content-Disposition le indica al navegador/cliente que debe
        # descargar el archivo en vez de mostrarlo directamente
        headers={"Content-Disposition": 'attachment; filename="personas.csv"'},
    )
