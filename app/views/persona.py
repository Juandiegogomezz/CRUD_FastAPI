"""
Modelos Pydantic (Esquemas) para la validación y serialización 
de datos de entrada y salida en los endpoints de la API.
"""
from datetime import date, datetime
from pydantic import BaseModel, Field, EmailStr


class PersonaBase(BaseModel):
    """Shared attributes for Persona inputs."""
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=30)
    birth_date: date | None = None
    is_active: bool = True
    notes: str | None = None


class PersonaCreate(PersonaBase):
    """Schema used for creating a new Persona."""
    pass


class PersonaUpdate(BaseModel):
    """Schema used for partial update of Persona."""
    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=30)
    birth_date: date | None = None
    is_active: bool | None = None
    notes: str | None = None


class PersonaRead(BaseModel):
    """Schema used to return Persona data to clients."""
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    phone: str | None
    birth_date: date | None
    is_active: bool
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class EdadEstadisticas(BaseModel):
    """Schema for age statistics computed from birth_date."""
    edad_promedio: float | None
    edad_minima: int | None
    edad_maxima: int | None


class PoblarRequest(BaseModel):
    """Schema used for the bulk population request."""
    # gt=0 y le=1000 validan automaticamente el rango permitido:
    # si se envia un valor fuera de este rango, FastAPI responde
    # con 422 Unprocessable Entity sin que tengamos que validarlo
    # manualmente en el endpoint
    cantidad: int = Field(..., gt=0, le=1000)
