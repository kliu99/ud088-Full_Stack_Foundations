import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Date, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class Shelter(Base):
	__tablename__ = "shelter"

	id = Column(Integer, primary_key = True, unique = True, autoincrement = True)
	name = Column(String, nullable = False)
	address = Column(String)
	city = Column(String)
	state = Column(String)
	zipCode = Column(Integer)
	website = Column(String)


class Puppy(Base):
	__tablename__ = "puppy"

	id = Column(Integer, primary_key = True, unique = True, autoincrement = True)
	name = Column(String, nullable = False)
	dateOfBirth = Column(Date)
	gender = Column(String)
	weight = Column(Float)
	shelter_id = Column(Integer, ForeignKey('shelter.id'))
	shelter = relationship(Shelter)
	picture = Column(String)


engine = create_engine('sqlite:///puppyshelter.db')

Base.metadata.create_all(engine)
