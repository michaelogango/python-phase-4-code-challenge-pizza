#!/usr/bin/env python3
from flask_migrate import Migrate
from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from models import db, Restaurant, RestaurantPizza, Pizza
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.json.compact = False

    db.init_app(app)
    Migrate(app, db)
    
    api = Api(app)

    @app.route("/")
    def index():
        return "<h1>Code Challenge</h1>"

    class RestaurantsResource(Resource):
        def get(self):
            restaurants = Restaurant.query.all()
            return [restaurant.to_dict(incl_pizzas=False) for restaurant in restaurants], 200

    # api.add_resource(RestaurantsResource, "/restaurants")

    class RestaurantByIdResource(Resource):
        def get(self, id):
            restaurant = Restaurant.query.get(id)
            if not restaurant:
                return {"error": "Restaurant not found"}, 404
            return restaurant.to_dict(incl_pizzas=True), 200

        def delete(self, id):
            restaurant = Restaurant.query.get(id)
            if not restaurant:
                return {"error": "Restaurant not found"}, 404
            db.session.delete(restaurant)
            db.session.commit()
            return {}, 204

    api.add_resource(RestaurantByIdResource, "/restaurants/<int:id>")

    class PizzasResource(Resource):
        def get(self):
            pizzas = Pizza.query.all()
            return [pizza.to_dict() for pizza in pizzas], 200

    api.add_resource(PizzasResource, "/pizzas")

    class RestaurantPizzasResource(Resource):
        def post(self):
            data = request.get_json()
            
            # Validate price range
            price = data.get("price")
            if not (1 <= price <= 30):
                return {"errors": ["validation errors"]}, 400
            
            restaurant = Restaurant.query.get(data.get("restaurant_id"))
            pizza = Pizza.query.get(data.get("pizza_id"))
            
            if not restaurant or not pizza:
                return {"errors": ["Invalid restaurant or pizza ID"]}, 400

            try:
                restaurant_pizza = RestaurantPizza(
                    price=price,
                    restaurant_id=data["restaurant_id"],
                    pizza_id=data["pizza_id"]
                )
                db.session.add(restaurant_pizza)
                db.session.commit()
                return restaurant_pizza.to_dict(), 201
            except Exception as e:
                return {"error": str(e)}, 400

    api.add_resource(RestaurantPizzasResource, "/restaurant_pizzas")

    return app

app = create_app()

if __name__ == "__main__":
    app.run(port=5555, debug=True)
