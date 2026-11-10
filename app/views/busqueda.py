from pydantic import BaseModel


class PersonaActivaRead(BaseModel):
    """Proyección reducida para GET /personas/reporte/activos."""
    id: int
    email: str
    phone: str | None
    is_active: bool

    model_config = {"from_attributes": True}


class BulkDesactivarRequest(BaseModel):
    """Body de PATCH /personas/bulk/desactivar. Lista de IDs a desactivar."""
    ids: list[int]
