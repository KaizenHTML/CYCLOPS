import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from src.infrastructure.database.session import Base

class IncidentModel(Base):
    """Modelo ORM para el registro de eventos y alertas detectadas por CYCLOPS."""
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    sender = Column(String(255), nullable=False, index=True)
    subject = Column(String(255), nullable=True)
    body_text = Column(Text, nullable=False)
    language = Column(String(10), default="es")
    
    # Metricas de analisis NLP y persuasión
    urgency_score = Column(Float, nullable=False, default=0.0)
    cialdini_principles = Column(String(255), nullable=True)
    has_suspicious_links = Column(Boolean, default=False)
    
    # Clasificacion del modelo
    prediction_label = Column(Integer, nullable=False)
    confidence = Column(Float, nullable=False)
    severity = Column(String(20), default="LOW")
    
    # Trazabilidad de tiempo y estado
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String(50), default="PENDING_REVIEW")

    def __repr__(self):
        return f"<Incident(id={self.id}, sender='{self.sender}', severity='{self.severity}')>"