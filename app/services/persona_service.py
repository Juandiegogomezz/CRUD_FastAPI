from typing import Sequence
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, text

import unicodedata
from faker import Faker
import csv
import io
from ..models.persona import Persona
from ..views.persona import PersonaCreate, PersonaUpdate
from .errors import PersonaNotFoundError, EmailAlreadyExistsError


def create_persona(db: Session, payload: PersonaCreate) -> Persona:
    """Create a Persona ensuring unique email."""
    # Optimistic check; DB unique constraint is the final guard
    if db.query(Persona).filter(Persona.email == payload.email).first():
        raise EmailAlreadyExistsError()
    obj = Persona(
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        phone=payload.phone,
        birth_date=payload.birth_date,
        is_active=payload.is_active,
        notes=payload.notes,
    )
    db.add(obj)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        # Catch race conditions on unique email
        raise EmailAlreadyExistsError() from e
    db.refresh(obj)
    return obj


def list_personas(db: Session, skip: int = 0, limit: int = 100) -> Sequence[Persona]:
    """Return paginated list of Personas."""
    return db.query(Persona).offset(skip).limit(limit).all()


def get_persona(db: Session, persona_id: int) -> Persona:
    """Return Persona by ID or raise if not found."""
    obj = db.query(Persona).filter(Persona.id == persona_id).first()
    if not obj:
        raise PersonaNotFoundError()
    return obj


def update_persona(db: Session, persona_id: int, payload: PersonaUpdate) -> Persona:
    """Update Persona partially, enforcing unique email."""
    obj = db.query(Persona).filter(Persona.id == persona_id).first()
    if not obj:
        raise PersonaNotFoundError()

    data = payload.model_dump(exclude_unset=True)
    if "email" in data and data["email"] != obj.email:
        if db.query(Persona).filter(Persona.email == data["email"], Persona.id != persona_id).first():
            raise EmailAlreadyExistsError()

    for field, value in data.items():
        setattr(obj, field, value)

    db.add(obj)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise EmailAlreadyExistsError() from e
    db.refresh(obj)
    return obj

def delete_persona(db: Session, persona_id: int) -> None:
    """Delete Persona by ID or raise if not found."""
    obj = db.query(Persona).filter(Persona.id == persona_id).first()
    if not obj:
        raise PersonaNotFoundError()
    db.delete(obj)
    db.commit()

    
def get_dominios_stats(db: Session) -> dict:
    """
    Calcula la distribución de personas por dominio de correo.
    Extrae el texto posterior al símbolo '@' y agrupa los resultados 
    para facilitar el análisis estadístico en el frontend.
    """
    dominio = func.substring_index(Persona.email, "@", -1)
    rows = (
        db.query(dominio, func.count(Persona.id))
        .group_by(dominio)
        .order_by(func.count(Persona.id).desc())
        .all()
    )
    return {nombre: total for nombre, total in rows}

def reset_personas(db: Session) -> int:
    """Delete all Personas and return how many were deleted."""
    # Contamos los registros ANTES de eliminarlos, porque despues
    # del delete ya no habria forma de saber cuantos habia
    cantidad = db.query(Persona).count()
    db.query(Persona).delete()
    db.commit()
    return cantidad

def _normalizar_para_email(texto: str) -> str:
    """Quita tildes, enes y caracteres especiales para usar en un email."""
    # NFKD descompone caracteres acentuados en su letra base + el acento
    # por separado (ej: "é" se separa en "e" + acento), lo que nos
    # permite despues descartar el acento y quedarnos solo con la letra
    texto_normalizado = unicodedata.normalize("NFKD", texto)
    solo_ascii = texto_normalizado.encode("ascii", "ignore").decode("ascii")
    return solo_ascii.lower()


def poblar_personas(db: Session, cantidad: int) -> int:
    """Generate and insert `cantidad` fake Personas with realistic data."""
    # Usamos la configuracion regional es_CO para que los nombres,
    # telefonos y textos generados tengan formato colombiano
    fake = Faker("es_CO")
    dominios = ["gmail.com", "outlook.com"]
    creados = 0

    for _ in range(cantidad):
        first_name = fake.first_name()
        last_name = fake.last_name()
        dominio = fake.random_element(dominios)
        # Normalizamos el nombre antes de construir el email para evitar
        # caracteres como tildes o la ñ, que no son validos en un email
        # (ej: "Jose" -> "jose", "Peña" -> "Pena")
        base_email = f"{_normalizar_para_email(first_name)}.{_normalizar_para_email(last_name)}"
        email = f"{base_email}@{dominio}"

        # Si el email ya existe, le agregamos un numero hasta que sea unico
        contador = 1
        while db.query(Persona).filter(Persona.email == email).first():
            email = f"{base_email}{contador}@{dominio}"
            contador += 1

        obj = Persona(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=fake.phone_number(),
            # Edad valida entre 18 y 85 anos, segun lo solicitado
            birth_date=fake.date_of_birth(minimum_age=18, maximum_age=85),
            is_active=fake.boolean(),
            # notes tiene 50% de probabilidad de quedar vacio (None)
            notes=fake.sentence() if fake.boolean() else None,
        )
        db.add(obj)
        creados += 1    

    db.commit()
    return creados
def exportar_personas_csv(db: Session):
    """Generate a CSV stream with all Personas (excluding created_at)."""
    personas = db.query(Persona).all()

    # Usamos StringIO para construir el CSV "en memoria", sin necesidad
    # de crear un archivo temporal en disco
    buffer = io.StringIO()
    writer = csv.writer(buffer)

    # Encabezado: solo los campos pedidos, sin incluir created_at
    writer.writerow(["id", "first_name", "last_name", "email", "phone", "birth_date", "is_active", "notes"])

    # Una fila por cada persona, en el mismo orden que el encabezado
    for p in personas:
        writer.writerow([
            p.id,
            p.first_name,
            p.last_name,
            p.email,
            p.phone,
            p.birth_date,
            p.is_active,
            p.notes,
        ])

    # Rebobinamos el buffer al inicio, para que la lectura posterior
    # (en StreamingResponse) empiece desde el principio del contenido
    buffer.seek(0)
    return buffer
