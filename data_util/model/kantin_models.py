from datetime import time
from typing import Any

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, create_engine, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_on = Column(DateTime(timezone=True), default=func.now())
    modified_on = Column(DateTime(timezone=True), default=func.now())

    def __init__(self, connection_string: str, **kw: Any):
        super().__init__(**kw)
        engine = create_engine(connection_string, echo=True)
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
        return f"<Franchise {self.franchise_name}>"


class MenuCategory(BaseModel):
    __tablename__ = "menu_categories"

    category_name = Column(String(45), nullable=False)
    description = Column(String(250), nullable=True)
    # menus = relationship("Menu", uselist=False, backref="menu_category_id", cascade="all, delete-orphan")

    def __init__(self, connection_string: str, **kw: Any):
        super().__init__(connection_string, **kw)
        self.category_name = kw.get("category_name")
        self.description = kw.get("description")

    def __repr__(self):
        return f"<MenuCategory {self.category_name}>"


class Menu(BaseModel):
    __tablename__ = "menus"

    menu_name = Column(String(45), nullable=False)
    description = Column(String(250), nullable=True)
    menu_category_id: int = Column(Integer, ForeignKey("menu_category.id"), nullable=False)
    # menu = relationship("MenuItem", uselist=False, backref="menu", cascade="all, delete-orphan")

    def __init__(self, connection_string: str, **kw: Any):
        super().__init__(connection_string, **kw)
        self.menu_name: str = kw.get("menu_name")
        self.description: str = kw.get("description")

    def __repr__(self):
        return f"<Menu {self.menu_name}>"


class MenuItem(BaseModel):
    __tablename__ = "menu_items"

    item_name: str = Column(String(45), nullable=False)
    item_price: float = Column(Float, nullable=False)
    description: str = Column(String(250), nullable=True)
    menu_id: int = Column(Integer, ForeignKey("menu.id"), nullable=False)

    def __init__(self, connection_string: str, **kw: Any):
        super().__init__(connection_string, **kw)
        self.item_name = kw.get("item_name")
        self.description = kw.get("description")
        self.item_price = kw.get("item_price")
        self.menu_id = kw.get("menu_id")

    def __repr__(self):
        return f"<MenuItem {self.item_name}>"


class RestaurantOwner(BaseModel):
    __tablename__ = "restaurant_owners"

    owner_name: str = Column(String(45), nullable=False)
    description: str = Column(String(250), nullable=True)
    restaurant = relationship("Restaurant", uselist=False, backref="owner", cascade="all, delete-orphan")

    def __init__(self, connection_string: str, **kw: Any):
        super().__init__(connection_string, **kw)
        self.owner_name = kw.get("owner_name")
        self.description = kw.get("description")

    def __repr__(self):
        return f"<RestaurantOwner {self.owner_name}>"


class Restaurant(BaseModel):
    __tablename__ = "restaurants"

    restaurant_name: str = Column(String(45), nullable=False)
    allow_pets: bool = Column(Boolean, nullable=False, default=True)
    closing_hour: time = Column(DateTime, nullable=True)
    opening_hour: time = Column(DateTime, nullable=True)
    has_smoking_area: bool = Column(Boolean, nullable=False, default=False)
    remarks: str = Column(String(200), nullable=False)
    restaurant_owner_id: int = Column(Integer, ForeignKey("restaurant_owners.id"), nullable=False)

    def __init__(self, connection_string: str, **kw: Any):
        super().__init__(connection_string, **kw)
        self.restaurant_name = kw.get("item_name")
        self.description = kw.get("description")
        self.item_price = kw.get("item_price")
        self.menu_id = kw.get("menu_id")

    def __repr__(self):
        return f"<MenuItem {self.restaurant_name}>"
