#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)
api = Api(app)

@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route('/restaurants', methods=['GET', 'DELETE'])
def restaurants():
    if request.method == 'GET':
        restaurants = []
        for restaurant in Restaurant.query.all():
            restaurant_dict = {
                'id': restaurant.id,
                'name': restaurant.name,
                'address': restaurant.address
            }
            restaurants.append(restaurant_dict)
        return make_response(jsonify(restaurants), 200)
    
    elif request.method == 'DELETE':
        Restaurant.query.delete()
        db.session.commit()
        return make_response(jsonify({"message": "All restaurants deleted"}), 200)

@app.route('/restaurants/<int:id>', methods=['GET', 'DELETE'])
def restaurant_by_id(id):
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        return make_response(jsonify({"error": "Restaurant not found"}), 404)
    
    if request.method == 'GET':
        restaurant_pizzas = [
            {
                'id': rp.id,
                'pizza': {
                    'id': rp.pizza.id,
                    'ingredients': rp.pizza.ingredients,
                    'name': rp.pizza.name
                },
                'pizza_id': rp.pizza_id,
                'price': rp.price,
                'restaurant_id': rp.restaurant_id
            }
            for rp in restaurant.restaurant_pizzas
        ]
        
        restaurant_dict = {
            'id': restaurant.id,
            'name': restaurant.name,
            'address': restaurant.address,
            'restaurant_pizzas': restaurant_pizzas
        }
        return make_response(jsonify(restaurant_dict), 200)
    
    elif request.method == 'DELETE':
        db.session.delete(restaurant)
        db.session.commit()
        return make_response(jsonify({}), 204)

@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = []
    for pizza in Pizza.query.all():
        pizza_dict = {
            'id': pizza.id,
            'ingredients': pizza.ingredients,
            'name': pizza.name
        }
        pizzas.append(pizza_dict)
    return make_response(jsonify(pizzas), 200)

@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.get_json()
    errors = []

    try:
        price = data['price']
        pizza_id = data['pizza_id']
        restaurant_id = data['restaurant_id']

        if not isinstance(price, (int, float)) or not (1 <= price <= 30):
            errors.append("validation errors") 

        pizza = Pizza.query.get(pizza_id)
        restaurant = Restaurant.query.get(restaurant_id)

        if not pizza:
            errors.append("validation errors")  
        
        if not restaurant:
            errors.append("validation errors")  

        if errors:
            return make_response(jsonify({"errors": errors}), 400)
        
        restaurant_pizza = RestaurantPizza(
            price=price,
            pizza_id=pizza_id,
            restaurant_id=restaurant_id
        )

        db.session.add(restaurant_pizza)
        db.session.commit()

        response_data = {
            'id': restaurant_pizza.id,
            'pizza': {
                'id': pizza.id,
                'ingredients': pizza.ingredients,
                'name': pizza.name
            },
            'pizza_id': pizza_id,
            'price': price,
            'restaurant': {
                'id': restaurant.id,
                'name': restaurant.name,
                'address': restaurant.address
            },
            'restaurant_id': restaurant_id
        }

        return make_response(jsonify(response_data), 201)

    except KeyError:
        return make_response(jsonify({"errors": ["validation errors"]}), 400)
    except Exception as e:
        return make_response(jsonify({"errors": ["validation errors"]}), 400)

if __name__ == "__main__":
    app.run(port=5555, debug=True)
