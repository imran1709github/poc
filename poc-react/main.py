from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy import create_engine, Column, Integer, String, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define the SQLite database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Create SQLAlchemy engine
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Define the base class for the database model
Base = declarative_base()

# Define the SQLAlchemy model
class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    isd_file_number = Column(String, unique=True, index=True)
    province = Column(String)
    reported_date = Column(Date)
    isd_investigator = Column(String)
    equite_support = Column(String, nullable=True)
    vin = Column(String)
    vehicle_year = Column(Integer)
    vehicle_make = Column(String)
    vehicle_model = Column(String)
    vehicle_model_line = Column(String, nullable=True)
    vehicle_condition = Column(String)
    acv = Column(Float)
    blackbook_acv = Column(Float)
    part_recovery = Column(Float, nullable=True)
    false_vin = Column(String, nullable=True)
    vehicle_theft_date = Column(Date)
    license_plate = Column(String, nullable=True)

# Create the database tables
Base.metadata.create_all(bind=engine)

# Create a FastAPI instance
app = FastAPI()

# Define the database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define Pydantic models
class VehicleCreate(BaseModel):
    isd_file_number: str
    province: str
    reported_date: str
    isd_investigator: str
    equite_support: Optional[str] = None
    vin: str
    vehicle_year: int
    vehicle_make: str
    vehicle_model: str
    vehicle_model_line: Optional[str] = None
    vehicle_condition: str
    acv: float
    blackbook_acv: float
    part_recovery: Optional[float] = None
    false_vin: Optional[str] = None
    vehicle_theft_date: str
    license_plate: Optional[str] = None

class VehicleInDB(VehicleCreate):
    id: int

    class Config:
        orm_mode = True

# CRUD operations
@app.post("/vehicles/", response_model=VehicleInDB)
def create_vehicle(vehicle: VehicleCreate):
    db = SessionLocal()
    db_vehicle = Vehicle(**vehicle.dict())
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    db.close()
    return db_vehicle

@app.get("/vehicles/", response_model=List[VehicleInDB])
def read_vehicles(skip: int = 0, limit: int = 10):
    db = SessionLocal()
    vehicles = db.query(Vehicle).offset(skip).limit(limit).all()
    db.close()
    return vehicles

@app.get("/vehicles/{vehicle_id}", response_model=VehicleInDB)
def read_vehicle(vehicle_id: int):
    db = SessionLocal()
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    db.close()
    if vehicle is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle


from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
