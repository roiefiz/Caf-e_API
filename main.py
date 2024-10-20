from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random
import requests

app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Café TABLE Configuration


class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=False)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


@app.route("/")
def home():
    api_docs = 'https://documenter.getpostman.com/view/25707180/2s93ecxARU#4c91c694-2776-42a4-a043-3079f5730f83'
    return render_template("index.html", docs=api_docs)


@app.route("/random", methods=["GET"])
def get_random_cafe():
    with app.app_context():
        all_cafes = db.session.query(Cafe).all()
        random_cafe = random.choice(all_cafes)
        return jsonify(cafe=random_cafe.to_dict())


@app.route("/all")
def all_cafes():
    with app.app_context():
        cafes = db.session.query(Cafe).all()
        return jsonify(cafes=[cafe.to_dict() for cafe in cafes])


@app.route("/search", methods=["GET"])
def search_coffee():
    search_location = request.args.get("loc")
    with app.app_context():
        cafe = db.session.query(Cafe).filter_by(location=search_location).first()
        if cafe:
            return jsonify(cafe=cafe.to_dict())
        else:
            return jsonify(error={"Not found: No coffee for you:"})


# POST - Create record
@app.route("/add", methods=["POST"])
def add_cafe():
    with app.app_context():
        print(request.args)
        new_cafe = Cafe(
            name=request.args.get('name'),
            img_url=request.args.get('img_url'),
            map_url=request.args.get('map_url'),
            location=request.args.get('location'),
            seats=request.args.get('seats'),
            has_toilet=bool(request.args.get('has_toilet')),
            has_wifi=bool(request.args.get('has_wifi')),
            has_sockets=bool(request.args.get('has_sockets')),
            can_take_calls=bool(request.args.get("can_take_calls")),
            coffee_price=request.args.get('coffee_price')
        )
        db.session.add(new_cafe)
        db.session.commit()
        return jsonify(m="Success: New Cafe was added")


# PATCH/PUT for updating record
@app.route("/update_price/<int:cafe_id>", methods=["PATCH", "PUT"])
def update_item(cafe_id):
    new_price = request.args.get("new_price")
    cafe = db.session.query(Cafe).get(cafe_id)
    if cafe:
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify(messege="Success: Successfully updated the price."), 200
    else:
        return jsonify(messege="Not Found: Sorry a coffee with that id was not found in the database"), 404


@app.route("/report_closed/<int:cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    api_inserted = request.args.get('api_key')
    cafe = db.session.query(Cafe).get(cafe_id)
    if cafe and api_inserted == "FizAPIKey":
        db.session.delete(cafe)
        db.session.commit()
        return jsonify(messege="Thank you! The cafe has been removed from the database"), 200
    elif cafe and api_inserted != "FizAPIKey":
        return jsonify(messege="Failed: Access denied. Check you API key and try again."), 403
    else:
        return jsonify(messege="Not Found: Cafe with that id was not found in the database"), 404


if __name__ == "__main__":
    app.run(debug=True)
