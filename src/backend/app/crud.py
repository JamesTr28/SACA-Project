from sqlalchemy.orm import Session
from . import models, schemas, security

# --- User CRUD ---
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = security.get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- Triage Session CRUD ---
def create_triage_session(db: Session, user_id: int, symptoms: list, disease: str, probability: float):
    db_session = models.TriageSession(
        user_id=user_id,
        symptoms_input={"symptoms": symptoms},
        predicted_disease=disease,
        prediction_probability=probability
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session
