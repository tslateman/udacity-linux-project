The purpose of this project is to use create an Item Catalog App.

The user will be able to view a catalog of items and browse by
category. Once they sign in they can also create and edit items.

This was written for the third project of the Udacity Full Stack 
Developer nanodegree.

The project is pretty straightforward and does much of any special
features. The main addition is the image feature. Also I added
some basic links to get around the site more easily.

-------------------------------------------------------------------

List Of Files

Be sure that you have saved in your directory the following files:

catalog.py
database_setup.py
db_populate.py
static/styles.css
static/bootstrap.css
templates/base.html
templates/catalog.html
templates/category.html
templates/deleteitem.html
templates/edititem.html
templates/item.html
templates/login.html
templates/newitem.html


There are other bootstrap files also, but at the very least
you will need what is above.

-------------------------------------------------------------------

Instructions For Usage

You will need to have Vagrant setup. For more help on that:

https://www.udacity.com/wiki/ud197/install-vagrant

Once you have vagrant, you will need to type the following commands:

vagrant up
vagrant ssh

This gets you to the virtual machine. From there you will need to 
navigate to the synced home directory. This should be as simple as
entering the following:

cd /vagrant/catalog

To test the code you will need to have Python installed first. 
This was created with 2.7.10, so if you want to match please select 
that version and install on your machine. Then to run the program,
navigate to the directory you saved the files and enter the following:
Once in the right directory, populate the database with

python db_populate.py

After populating the database run the following command to start the app

python catalog.py

Then open a browser and navigate to "http://localhost:5000/"

The JSON for the items is located at:

http://localhost:5000//catalog/items/JSON

-------------------------------------------------------------------

Some of the code from this course was based on lessons taught in
the Udacity Full Stack Foundations course and the Authentication
and Authorization course. The code was modified to meet the 
requirements set by the Udacity project 3 rubric.
