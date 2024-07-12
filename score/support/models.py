from sqlalchemy import Column, Integer, Float, String, DateTime
from support.database import Base


# database table classes
class CovalentTable(Base):

    __tablename__ = 'covalent'

    event_id = Column(Integer, primary_key=True)
    datetime = Column(DateTime, nullable=False)
    amount_requested = Column(Float, nullable=False)
    credit_score = Column(Float, nullable=False)
    amount_granted = Column(Float, nullable=False)
    loan_risk = Column(String, nullable=False)
