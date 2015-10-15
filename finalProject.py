"""import Flask framework"""
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
app = Flask(__name__)

"""import CRUD operations from SQLalchemy"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

"""connect to database and create session"""

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind=engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

"""show all restaurants"""
@app.route('/')
@app.route('/restaurants')
def showRestaurants():
	restaurants = session.query(Restaurant).all()
	if restaurants == []:
		return render_template('emptyrestaurants.html')
	else:
		return render_template('restaurants.html', restaurants = restaurants)

"""make a new restaurant"""
@app.route('/restaurant/new', methods=['GET','POST'])
def newRestaurant():
	if request.method == 'POST':
		newRestaurant = Restaurant(name=request.form['name'])
		session.add(newRestaurant)
		session.commit()
		flash("New restaurant created!")
		return redirect(url_for('showRestaurants'))
	else:
		return render_template('newrestaurant.html')

"""edit a restaurant"""
@app.route('/restaurant/<int:restaurant_id>/edit', methods=['GET','POST'])
def editRestaurant(restaurant_id):

	editedRestaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()

	if request.method == 'POST':
		
		if request.form['name']:
			editedRestaurant.name = request.form['name']

		session.add(editedRestaurant)
		session.commit()
		flash("Restaurant successfully edited!")
		return redirect(url_for('showRestaurants'))
	else:
		return render_template('editrestaurant.html', restaurant = editedRestaurant)


"""delete a restaurant"""
@app.route('/restaurant/<int:restaurant_id>/delete', methods=['GET','POST'])
def deleteRestaurant(restaurant_id):
	deletedRestaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
	if request.method == 'POST':
		if request.form['delete_item']:
			session.delete(deletedRestaurant)
			session.commit()
			flash("Restaurant successfully deleted!")
		return redirect(url_for('showRestaurants', restaurant_id=restaurant_id))
	else:
		return render_template('deleterestaurant.html', restaurant = deletedRestaurant)


"""show the menu of a restaurant"""
@app.route('/restaurant/<int:restaurant_id>/menu')
def showMenu(restaurant_id):
	restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
	items = session.query(MenuItem).filter_by(restaurant_id = restaurant.id)
	"""item = session.query(MenuItem).filter_by(id = menuitem_id).one()"""
	if items == []:
		return render_template('emptymenus.html')
	else:
		return render_template('menu.html', restaurant = restaurant, items = items)


"""make a new menu item for a restaurant"""
@app.route('/restaurant/<int:restaurant_id>/menu/new', methods=['GET','POST'])
def newMenuItem(restaurant_id):
	restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
	if request.method == 'POST':
		newItem = MenuItem(name=request.form['name'], restaurant_id=restaurant_id)
		session.add(newItem)
		session.commit()
		flash("Menu item created!")
		return redirect(url_for('showMenu', restaurant_id=restaurant_id))
	else:
		return render_template('newmenuitem.html', restaurant = restaurant)

"""edit an existing menu item for a restaurant"""
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit', methods=['GET','POST'])
def editMenu(restaurant_id, menu_id):
	restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
	editedItem = session.query(MenuItem).filter_by(id=menu_id).one()
	if request.method == 'POST':
		if request.form['name']:
			editedItem.name = request.form['name']
		session.add(editedItem)
		session.commit()
		flash("Menu item successfully edited!")
		return redirect(url_for('showMenu', restaurant_id=restaurant_id))
	else:
		return render_template('editmenuitem.html', restaurant = restaurant, item = editedItem)

"""delete an existing menu item for a restaurant"""
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete', methods=['GET','POST'])
def deleteMenu(restaurant_id, menu_id):
	restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
	deletedItem = session.query(MenuItem).filter_by(id=menu_id).one()
	if request.method == 'POST':
		if request.form['name']:
			session.delete(deletedItem)
			session.commit()
			flash("Menu item deleted!")
		return redirect(url_for('showMenu', restaurant_id=restaurant_id))
	else:
		return render_template('deletemenuitem.html', restaurant = restaurant, item = deletedItem)

"""API for restaurant list"""
@app.route('/restaurants/JSON')
def restaurantJSON():
    restaurants = session.query(Restaurant).all()
    return jsonify(restaurants=[r.serialize for r in restaurants])

"""API for restaurant menu"""
@app.route('/restaurant/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
    return jsonify(MenuItems=[i.serialize for i in items])

"""API for menu item"""
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_item_id>/JSON')
def menuItemJSON(restaurant_id, menu_item_id):
    item = session.query(MenuItem).filter_by(id=menu_item_id).one()
    return jsonify(MenuItem=item.serialize)

if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)