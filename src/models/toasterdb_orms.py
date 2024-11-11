from sqlalchemy import Column
from sqlalchemy.types import INT, VARCHAR
from sqlalchemy.orm import relationship, DeclarativeBase

class Base(DeclarativeBase):
    pass

class ShippingInfo(Base):
    __tablename__ = 'SHIPPING_INFO'

    id = Column(INT, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(45), nullable=True)
    address_1 = Column(VARCHAR(45), nullable=True)
    address_2 = Column(VARCHAR(45), nullable=True)
    city = Column(VARCHAR(45), nullable=True)
    state = Column(VARCHAR(45), nullable=True)
    zip = Column(VARCHAR(45), nullable=True)

    orders = relationship("CustomerOrder", back_populates="shipping_info")
