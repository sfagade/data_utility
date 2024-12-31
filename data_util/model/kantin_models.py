from typing import Any

from sqlalchemy import Column, DateTime, Integer, String, create_engine, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_on = Column(DateTime(timezone=True), default=func.now())
    modified_on = Column(DateTime(timezone=True), default=func.now())

    def __init__(self, connection_string: str, **kw: Any):
        super().__init__(**kw)
        engine = create_engine(connection_string)
        session_maker = sessionmaker(bind=engine)
        self.session = session_maker()

    def create(self):
        self.session.add(self)
        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e
        return self

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get(id)


class FoodType(BaseModel):
    __tablename__ = "food_types"

    type_name = Column(String(25), nullable=False)
    description = Column(String(250), nullable=True)

    def __init__(self, connection_string: str, **kw: Any):
        super().__init__(connection_string, **kw)
        self.type_name = kw.get("type_name")
        self.description = kw.get("description")

    def __repr__(self):
        return f"<FoodType {self.type_name}>"


class Franchise(BaseModel):
    __tablename__ = "franchises"

    franchise_name = Column(String(45), nullable=False)
    description = Column(String(250), nullable=True)

    def __init__(self, connection_string: str, **kw: Any):
        super().__init__(connection_string, **kw)
        self.franchise_name = kw.get("franchise_name")
        self.description = kw.get("description")

    def __repr__(self):
        return f"<FoodType {self.franchise_name}>"
