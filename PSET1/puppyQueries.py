from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from puppies import Base, Shelter, Puppy
from sqlalchemy import func

import datetime

engine = create_engine('sqlite:///puppyshelter.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()


#
# Query all of the puppies and return the results in ascending alphabetical order
def query_one():
    puppies = session.query(Puppy).order_by(Puppy.name.asc()).all()

    for puppy in puppies:
        print puppy.name

query_one()


#
# Query all of the puppies that are less than 6 months old organized by the youngest first
def query_two():
    today = datetime.date.today()
    days_old = 6*30
    birthday = today - datetime.timedelta(days = days_old)

    puppies = session.query(Puppy).filter("birthday >= %s" % birthday).order_by(Puppy.name.desc()).all()


    for puppy in puppies:
        print(puppy.name + ", " + str(puppy.dateOfBirth))

query_two()


#
# Query all puppies by ascending weight
def query_three():

    puppies = session.query(Puppy).order_by(Puppy.weight.asc()).all()

    for puppy in puppies:
        print "{name}: {weight}".format(name = puppy.name, weight = puppy.weight)

query_three()


#
# Query all puppies grouped by the shelter in which they are staying
def query_four():
    

    # SELECT Shelter.*, count(Puppy.id) as num 
    # FROM Shelter JOIN Puppy ON Shelter.id = Puppy.shelter_id 
    # GROUP BY Shelter.id

    result = session.query(Shelter, func.count(Puppy.id)).join(Puppy).group_by(Shelter.id).all()
    for item in result:
        print item[0].id, item[0].name, item[1]

query_four()