from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)
app.app_context().push()
# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)



# Cafe TABLE Configuration class + methods

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
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        # Method 1.
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            # Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            dictionary[column.name] = getattr(self, column.name)
        return dictionary

        # Method 2. Altenatively use Dictionary Comprehension to do the same thing.
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


@app.route("/random/")
def get_random_cafe():
    cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(cafes)
    return jsonify(cafe={
        "id": random_cafe.id,
        "name": random_cafe.name,
        "map_url": random_cafe.map_url,
        "img_url": random_cafe.img_url,
        "location": random_cafe.location,
        "seats": random_cafe.seats,
        "has_toilet": random_cafe.has_toilet,
        "has_wifi": random_cafe.has_wifi,
        "has_sockets": random_cafe.has_sockets,
        "can_take_calls": random_cafe.can_take_calls,
        "coffee_price": random_cafe.coffee_price,
    })


@app.route("/")
def home():
    url = "https://web.postman.co/workspace/a9c0054c-c1d5-44f1-8b10-3b6f93709473/documentation/27144821-c8a6483c-6b7a-452c-8a39-cdb45483db74?entity=&branch=&version="
    return render_template("index.html",url=url)

@app.route("/all")
def get_all_cafes():
    cafes = db.session.query(Cafe).all()
    #This uses a List Comprehension but you could also split it into 3 lines.
    return jsonify(cafes=[cafe.to_dict() for cafe in cafes])

@app.route("/search")
def get_cafe_at_location():
    query_location = request.args.get("loc")
    cafe = db.session.query(Cafe).filter_by(location=query_location).first()
    if cafe:
        return jsonify(cafe=cafe.to_dict())
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."})



def str_to_bool(arg_from_url):
    if arg_from_url in ['True', ' true', 'T', 't', 'Yes', 'yes', 'y', '1']:
        return True
    else:
        return False

@app.route("/add", methods=["GET", "POST"])
def add_a_cafe():
    new_cafe = Cafe(name=request.args.get("name"),
                    map_url=request.args.get("map_url"),
                    img_url=request.args.get("img_url"),
                    location=request.args.get("location"),
                    seats=request.args.get("seats"),
                    has_toilet=str_to_bool(request.args.get("has_toilet")),
                    has_wifi=str_to_bool(request.args.get("has_wifi")),
                    has_sockets=str_to_bool(request.args.get("has_sockets")),
                    can_take_calls=str_to_bool(request.args.get("can_take_calls")),
                    coffee_price=request.args.get("coffee_price")
                    )
    db.session.add(new_cafe)
    db.session.commit()

    return jsonify(response={"success": "Successfully added the new cafe"})

@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
def patch_new_price(cafe_id):
    new_price = request.args.get("new_price")
    cafe = db.session.query(Cafe).get(cafe_id)
    if cafe:
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the price."})
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."})

@app.route("/report-closed/<int:cafe_id>",methods=["DELETE"])
def delete_cafe(cafe_id):
    if request.args.get("api-key") == "1234":
        if Cafe.query.get(cafe_id) :
            cafe_to_delete = Cafe.query.get(cafe_id)
            db.session.delete(cafe_to_delete)
            db.session.commit()
            return jsonify(response={"success": "Successfully deleted the cafe."})
        else:
            return jsonify(error={"Not Found": "we didint found that id."})

    else:
        return jsonify(error={"Not Found": "Sorry thats a wrong api key."})

    # HTTP GET - Read Record

# HTTP POST - Create Record

# HTTP PUT/PATCH - Update Record

# HTTP DELETE - Delete Record


if __name__ == '__main__':
    app.run(debug=True)