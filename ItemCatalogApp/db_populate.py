from sqlalchemy import create_engine	
from sqlalchemy.orm import sessionmaker

from database_setup import Catalog, Base, User, Item

engine = create_engine('postgresql://catalog:release@localhost/catalog')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# If things get wonky, clear the item catalog with the following
"""
items = session.query(Item)
for item in items:
	session.delete(item)
	session.commit()

categories = session.query(Catalog)
for category in categories:
	session.delete(category)
	session.commit()
"""
	
# Create sample user
User1 = User(name="Any User", email="auser@email.com",
             picture='https://static.pexels.com/photos/8482/animal-dog-pet-indoors-large.jpg')
session.add(User1)
session.commit()

# Create Catalog
Category1 = Catalog(category="Dog Apparel", user=User1)
session.add(Category1)
session.commit()

# Create Items
Item1 = Item(name="Dog Collar", description="Hello! Doesn't my dog collar look fantastic?!",
			img_url="https://static.pexels.com/photos/8482/animal-dog-pet-indoors-large.jpg", 
			catalog=Category1, user=User1)
session.add(Item1)
session.commit()

Item2 = Item(name="Party Supplies", description="Hello! Party supplies are a must. I love parties!",
			img_url="https://static.pexels.com/photos/6460/garden-party-animal-dog-large.jpg", 
			catalog=Category1, user=User1)
session.add(Item2)
session.commit()

Category2 = Catalog(category="Home Stuff", user=User1)
session.add(Category2)
session.commit()

Item3 = Item(name="Chair", description="The long lost comfortable chair",
			img_url="https://static.pexels.com/photos/2051/sea-holiday-vacation-table-medium.jpg", 
			catalog=Category2, user=User1)
session.add(Item3)
session.commit()

Item4 = Item(name="Wine Glasses", description="Every house needs a set",
			img_url="https://static.pexels.com/photos/2141/alcohol-party-dinner-drink-large.jpg", 
			catalog=Category2, user=User1)
session.add(Item4)
session.commit()

print "Added Items!"
