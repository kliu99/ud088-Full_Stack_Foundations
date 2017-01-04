from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, exc
from database_setup import Base, Restaurant, MenuItem

app = Flask(__name__)

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


#
# Restaurants
@app.route('/')
@app.route('/restaurants/')
def mainPage():
    
    restaurants = list()
    restaurantQuery = session.query(Restaurant).all()

    for restaurant in restaurantQuery:
        r = dict()
        r['id'] = restaurant.id
        r['name'] = restaurant.name
        r['courses'] = session.query(func.count(MenuItem.id)).add_column(MenuItem.course). \
            filter_by(restaurant_id=restaurant.id).group_by(MenuItem.course).order_by(MenuItem.course.asc()).all()
        r['avgPrice'] = render_price(restaurant)

        restaurants.append(r)

    return render_template('front.html', restaurants=restaurants)


def render_price(restaurant):
    price = session.query(func.avg(MenuItem.price)).filter_by(restaurant_id=restaurant.id).one()[0]
    if price:
        price = float(price)
        if price < 5.:
            return "$"
        elif price < 10.:
            return "$$"
        else:
            return "$$$"
    return "$"

@app.route('/restaurants/new/', methods=['GET', 'POST'])
def restaurantNew():
    """ """
    if request.method == 'POST':
        name = request.form['name']
        if name:
            newRestaurant = Restaurant(name=name)
            session.add(newRestaurant)
            session.commit()
            
            flash("New Restaurant Created", "restaurant")
            return redirect(url_for('mainPage'))
    else:
        return render_template('restaurantNew.html')


@app.route('/restaurants/<int:restaurant_id>/edit/', methods=['GET', 'POST'])
def restaurantEdit(restaurant_id):
    """ """
    try:
        restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()

        if request.method == 'POST':
            name = request.form['name']
            if name:
                restaurant.name = name
                session.add(restaurant)
                session.commit()

                flash('Restaurant Successfully Edited', 'restaurant')
                return redirect(url_for('mainPage'))
        else:
            return render_template('restaurantEdit.html', restaurant=restaurant)

    except exc.NoResultFound:   
        return redirect(url_for('mainPage'))


@app.route('/restaurants/<int:restaurant_id>/delete/', methods=['GET', 'POST'])
def restaurantDelete(restaurant_id):
    """ """
    try:
        restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
        menuItems = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()

        if request.method == 'POST':
            for menuItem in menuItems:
                session.delete(menuItem)

            session.delete(restaurant)
            session.commit()

            flash('Restaurant Successfully Deleted', 'restaurant')
            return redirect(url_for('mainPage'))
        else:
            return render_template('restaurantDelete.html', restaurant=restaurant)

    except exc.NoResultFound:
            return redirect(url_for('mainPage'))


@app.route('/restaurants/JSON/')
def restaurantJson():
    """ """
    try:
        restaurants = session.query(Restaurant).all()
        return jsonify(Restaurants=[restaurant.serialize for restaurant in restaurants])
    except exc.NoResultFound:
        return redirect(url_for('mainPage'))


#
# Menus
@app.route('/restaurants/<int:restaurant_id>/')
@app.route('/restaurants/<int:restaurant_id>/menu/')
def restaurantMenu(restaurant_id):
    """ List all the menu for specific restaurant """
    try:
        restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
        menuItemsQuery = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).order_by(MenuItem.course.asc()).all()

        menuItems = dict()
        for m in menuItemsQuery:
            l = menuItems.get(m.course, list())
            l.append(m)
            menuItems[m.course] = l

        return render_template('restaurantMenu.html', restaurant=restaurant, menuItems=menuItems)

    except exc.NoResultFound:
        return redirect(url_for('mainPage'))


@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/')
def restaurantMenuItem(restaurant_id, menu_id):
    """ List all the menu for specific restaurant """

    return "List menu item " + str(menu_id) + " for " + str(restaurant_id)


@app.route('/restaurants/<int:restaurant_id>/menu/new/', methods=['GET', 'POST'])
def restaurantMenuItemNew(restaurant_id):
    """ List all the menu for specific restaurant """
    try:
        restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
        if request.method == 'POST':
            if request.form['name']:
                newItem = MenuItem(name=request.form['name'], description=request.form[
                                       'description'], price=request.form['price'], course=request.form['course'], restaurant_id=restaurant_id)
                session.add(newItem)
                session.commit()

                flash('Menu Item Created', 'menu')
                return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
        else:
            return render_template('menuItemNew.html', restaurant=restaurant)

    except exc.NoResultFound:
            return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))


@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/edit/', methods=['GET', 'POST'])
def restaurantMenuItemEdit(restaurant_id, menu_id):
    """ List all the menu for specific restaurant """
    try:
        restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
        menuItem = session.query(MenuItem).filter_by(id=menu_id).one()
        if request.method == 'POST':
            if request.form['name']:
                menuItem.name = request.form['name']
            if request.form['description']:
                menuItem.description = request.form['description']
            if request.form['price']:
                menuItem.price = request.form['price']
            if request.form['course']:
                menuItem.course = request.form['course']

            session.add(menuItem)
            session.commit()

            flash('Menu Item Successfully Edited', 'menu')
            return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
        else:
            return render_template('menuItemEdit.html', menuItem=menuItem, restaurant=restaurant)

    except exc.NoResultFound:
            return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))


@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/delete/', methods=['GET', 'POST'])
def restaurantMenuItemDelete(restaurant_id, menu_id):
    """ List all the menu for specific restaurant """
    try:
        restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
        menuItem = session.query(MenuItem).filter_by(id=menu_id).one()
        if request.method == 'POST':
            session.delete(menuItem)
            session.commit()

            flash('Menu Item Successfully Deleted', 'menu')
            return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
        else:
            return render_template('menuItemDelete.html', menuItem=menuItem, restaurant=restaurant)

    except exc.NoResultFound:
            return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))


@app.route('/restaurants/<int:restaurant_id>/menu/JSON/')
def restaurantMenuJson(restaurant_id):
    """ List all the menu for specific restaurant """
    try:
        menuItems = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
        return jsonify(MenuItems=[menuItem.serialize for menuItem in menuItems])
    except exc.NoResultFound:
        return redirect(url_for('mainPage'))


@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON/')
def restaurantMenuItemJson(restaurant_id, menu_id):
    """ List all the menu for specific restaurant """
    try:
        restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
        menuItem = session.query(MenuItem).filter_by(id=menu_id).one()
        return jsonify(MenuItem=[menuItem.serialize])
    except exc.NoResultFound:
        return redirect(url_for('mainPage'))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)