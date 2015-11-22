from flask import Flask, render_template, request, redirect, jsonify, url_for, flash

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Catalog, User, Item

from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
from flask.ext.seasurf import SeaSurf

import logging, sys
logging.basicConfig(stream=sys.stderr)

app = Flask(__name__)
app.secret_key = 'DunYbdwXfcdWd_NzzSX7vciP'
#app.config['sqlite:///catalog.db'] = 'postgresql://catalog:release@localhost/catalog'
#db = SQLAlchemy(app)
csrf = SeaSurf(app)

CLIENT_ID = json.loads(
    open('/var/www/ItemCatalogApp/client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Catalog App"

# Connect to Database and create database session
engine = create_engine('postgresql://catalog:release@localhost/catalog')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/catalog/items/JSON')
def itemsJSON():
    items = session.query(Item).all()
    return jsonify(Items=[i.serialize for i in items])


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)

@csrf.exempt
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('/var/www/ItemCatalogApp/client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # See if a user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
        # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash("Thanks! You've been logged Out")
        return redirect(url_for('showCatalog'))
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Decorator Function
def login_check():
    if 'username' in login_session:
        return
    else:
        return redirect(url_for("login"))

# Show Catalog
@app.route('/')
@app.route('/catalog/')
def showCatalog():
    catalog = session.query(Catalog).order_by(asc(Catalog.category))
    items = session.query(Item).all()
    username = ""
    if 'username' in login_session:
        username = login_session['username']
    return render_template('catalog.html', items=items, catalog=catalog,
        username=username, title='Catalog Page')

# Create a new item
@app.route('/catalog/newitem/', methods=['GET', 'POST'])
def newItem():
    login_check()
    username = "" 
    username = login_session['username']
    catalog = session.query(Catalog).order_by(asc(Catalog.category))
    if request.method == 'POST':
        newItem = Item(name=request.form['name'],
            description = request.form['description'],
        	user_id=login_session['user_id'],
            catalog_id=request.form['category'],
            img_url=request.form['img_url'])
        session.add(newItem)
        flash('New Item %s Successfully Created' % newItem.name)
        session.commit()
        return redirect(url_for('showCatalog'))
    else:
        return render_template('newitem.html', catalog=catalog, 
            username=username, title="New Item")

# Show a category of items
@app.route('/catalog/<int:category_id>/')
def showCategory(category_id):
    catalog = session.query(Catalog).order_by(asc(Catalog.category))
    category = session.query(Catalog).get(category_id)
    items = session.query(Item).filter_by(
        catalog_id=category_id).all()
    username = ""
    if 'username' in login_session:
        username = login_session['username']
    return render_template('category.html', items=items, category=category,
                            catalog=catalog, username=username, 
                            title='Category Page')

# Show item
@app.route('/catalog/item/<int:item_id>')
def showItem(item_id):
    catalog = session.query(Catalog).order_by(asc(Catalog.category))
    item = session.query(Item).get(item_id)
    username = ""
    if 'username' in login_session:
        username = login_session['username']
    return render_template('item.html', item=item, catalog=catalog,
                        username=username, title='Catalog Items')
# Edit item
@app.route('/catalog/item/<int:item_id>/edit', methods=['GET', 'POST'])
def editItem(item_id):
    login_check()
    username = login_session['username']
    editedItem = session.query(Item).filter_by(id=item_id).one()
    catalog = session.query(Catalog).order_by(asc(Catalog.category))
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['category']:
            editedItem.catalog_id = request.form['category']
        if request.form['img_url']:
            editedItem.img_url = request.form['img_url']
        session.add(editedItem)
        session.commit()
        flash('Catalog Item Successfully Edited')
        return redirect(url_for('showItem', item_id=item_id))
    else:
        return render_template('edititem.html', catalog=catalog, item=editedItem,
                            username=username, title='Edit Item')

# Delete a menu item
@app.route('/catalog/item/<int:item_id>/delete', methods=['GET', 'POST'])
def deleteItem(item_id):
    login_check()
    username = login_session['username']
    itemToDelete = session.query(Item).filter_by(id=item_id).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Item Successfully Deleted')
        return redirect(url_for('showCatalog'))
    else:
        return render_template('deleteItem.html', item=itemToDelete,
                            username=username, title='Delete Item')


if __name__ == '__main__':
    app.secret_key = 'DunYbdwXfcdWd_NzzSX7vciP'
    app.debug = True
    app.run(host='0.0.0.0', port=8080)

