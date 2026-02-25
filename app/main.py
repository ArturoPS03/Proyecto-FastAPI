from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="API Venta de Entradas")


@app.get("/")
def root():
    return {"mensaje": "API de Venta de Entradas Operativa 🎟️"}


# CRUD de Recintos

@app.post("/recintos/", response_model=schemas.Recinto)
def crear_recinto(recinto: schemas.RecintoCreate, db: Session = Depends(get_db)):
    db_recinto = models.Recinto(**recinto.dict())
    db.add(db_recinto)
    db.commit()
    db.refresh(db_recinto)
    return db_recinto


@app.get("/recintos/")
def listar_recintos(db: Session = Depends(get_db)):
    return db.query(models.Recinto).all()


@app.put("/recintos/{id}")
def actualizar_recinto(id: int, recinto: schemas.RecintoCreate, db: Session = Depends(get_db)):
    db_recinto = db.query(models.Recinto).get(id)
    if not db_recinto:
        raise HTTPException(status_code=404, detail="Recinto no encontrado")

    for key, value in recinto.dict().items():
        setattr(db_recinto, key, value)

    db.commit()
    return db_recinto


@app.delete("/recintos/{id}")
def eliminar_recinto(id: int, db: Session = Depends(get_db)):
    db_recinto = db.query(models.Recinto).get(id)
    if not db_recinto:
        raise HTTPException(status_code=404, detail="Recinto no encontrado")

    db.delete(db_recinto)
    db.commit()
    return {"mensaje": "Recinto eliminado"}


# CRUD de eventos

@app.post("/eventos/", response_model=schemas.Evento)
def crear_evento(evento: schemas.EventoCreate, db: Session = Depends(get_db)):
    db_evento = models.Evento(**evento.dict())
    db.add(db_evento)
    db.commit()
    db.refresh(db_evento)
    return db_evento


@app.get("/eventos/")
def listar_eventos(ciudad: str = None, db: Session = Depends(get_db)):
    query = db.query(models.Evento).join(models.Recinto)

    if ciudad:
        query = query.filter(models.Recinto.ciudad.ilike(f"%{ciudad}%"))

    return query.all()


@app.patch("/eventos/{id}/comprar")
def comprar_tickets(id: int, compra: schemas.CompraRequest, db: Session = Depends(get_db)):
    evento = db.query(models.Evento).get(id)

    if not evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")

    recinto = evento.recinto

    if evento.tickets_vendidos + compra.cantidad > recinto.capacidad:
        raise HTTPException(status_code=400, detail="Aforo insuficiente en el recinto")

    evento.tickets_vendidos += compra.cantidad
    db.commit()
    db.refresh(evento)

    return {"mensaje": "Compra realizada con éxito", "tickets_vendidos": evento.tickets_vendidos}
