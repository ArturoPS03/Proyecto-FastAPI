from pydantic import BaseModel, Field
from datetime import datetime

class RecintoBase(BaseModel):
    nombre: str
    ciudad: str
    capacidad: int

class RecintoCreate(RecintoBase):
    pass

class Recinto(RecintoBase):
    id: int
    class Config:
        orm_mode = True


class EventoBase(BaseModel):
    nombre: str
    fecha: datetime
    precio: float = Field(..., ge=0)
    recinto_id: int

class EventoCreate(EventoBase):
    pass

class Evento(EventoBase):
    id: int
    tickets_vendidos: int
    class Config:
        orm_mode = True


class CompraRequest(BaseModel):
    cantidad: int
