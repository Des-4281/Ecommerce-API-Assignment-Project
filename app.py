import os
from urllib.parse import quote_plus
from dotenv import load_dotenv 
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy 
from flask_marshmallow import Marshmallow
from datetime import datetime

load_dotenv()
#create app and establish connection to database in mysql local workbench 
app = Flask(__name__)
db_password = quote_plus(os.environ['DB_PASSWORD'])
app.config['SQLALCHEMY_DATABASE_URI'] = ( 
    f'mysql+mysqlconnector://root:{db_password}@localhost/ecommerce_api'
)
#create database helpers and api helpers 
db = SQLAlchemy(app)
ma = Marshmallow(app)

#create association table, taking the ids from orders and products table to form a record of products for each order and order number
order_product = db.Table( 
    'order_product',
    db.Column('order_id', db.Integer, db.ForeignKey('orders.id'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('products.id'), primary_key=True)
)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(225))
    address = db.Column(db.String(225))
    email = db.Column(db.String(225), unique=True)

    orders = db.relationship('Order', backref='user', lazy=True, cascade='all, delete')

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(225))
    price = db.Column(db.Float)

class Order(db.Model): 
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    products = db.relationship('Product', secondary=order_product, backref='orders')


with app.app_context():
    db.create_all()

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User

class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Product

class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Order
        include_fk = True

user_schema = UserSchema()
users_schema = UserSchema(many=True)
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)
order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)
# User Crud Routes

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return users_schema.jsonify(users)

@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get_or_404(id)
    return user_schema.jsonify(user)

@app.route('/users', methods=['POST'])
def create_user():
    data = request.json

    if 'name' not in data or 'email' not in data:
        return jsonify({'error': 'Name or Email are required'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400

    new_user = User(name=data['name'], address=data.get('address'), email=data['email'])
    db.session.add(new_user) 
    db.session.commit()  
    return user_schema.jsonify(new_user), 201


@app.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    user = User.query.get_or_404(id)
    data = request.json   
    user.name = data.get('name', user.name)
    user.address = data.get('address', user.address)
    user.email = data.get('email', user.email)
    db.session.commit()
    return user_schema.jsonify(user)

@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user) 
    db.session.commit()
    return jsonify({'message': f'User #{id} was deleted successfully'}), 200




# Product Crud Routes


@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return products_schema.jsonify(products)

@app.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    product = Product.query.get_or_404(id)
    return product_schema.jsonify(product)

@app.route('/products', methods=['POST'])
def create_product():
    data = request.json

    if 'product_name' not in data or 'price' not in data:
        return jsonify({'error': 'Product Name and Price are required'}), 400

    new_product = Product(product_name=data['product_name'], price=data['price'])
    db.session.add(new_product) 
    db.session.commit()  
    return product_schema.jsonify(new_product), 201


@app.route('/products/<int:id>', methods=['PUT'])
def update_products(id):
    product = Product.query.get_or_404(id)
    data = request.json   
    product.product_name = data.get('product_name', product.product_name)
    product.price = data.get('price', product.price)
    db.session.commit()
    return product_schema.jsonify(product)

@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product) 
    db.session.commit()
    return jsonify({'message': f'#{id}:{product.product_name} was deleted successfully'}), 200

# Order CRUD Routes

@app.route('/orders', methods=['POST'])
def create_order():
    data = request.json
    user = User.query.get_or_404(data['user_id'])
    order_date = datetime.fromisoformat(data['order_date']) if data.get ('order_date') else datetime.utcnow()

    new_order = Order(user_id=user.id, order_date=order_date)
    db.session.add(new_order) 
    db.session.commit()  
    return order_schema.jsonify(new_order), 201


@app.route('/orders/<int:order_id>/add_product/<int:product_id>', methods=['PUT'])
def add_product_to_order(order_id, product_id):
    order = Order.query.get_or_404(order_id)
    product = Product.query.get_or_404(product_id)

    if product in order.products:
        return jsonify({'message': 'Product already on this order'}), 400

    order.products.append(product)
    db.session.commit()
    return products_schema.jsonify(order.products)

@app.route('/orders/<int:order_id>/remove_product/<int:product_id>', methods=['DELETE'])
def remove_product_from_order(order_id, product_id):
    order = Order.query.get_or_404(order_id)
    product = Product.query.get_or_404(product_id)
    
    if product in order.products:
        order.products.remove(product)
        db.session.commit()
        return jsonify({'message': f'Product {product.id} was removed from the order #{order_id}'}), 200
    else:
        return jsonify({'error': f'Product {product.id}: is not on this order #{order_id}'}), 400

@app.route('/orders/user/<int:user_id>', methods=['GET'])
def get_orders_for_user(user_id):
    user = User.query.get_or_404(user_id)
    return orders_schema.jsonify(user.orders)

@app.route('/orders/<int:order_id>/products', methods=['GET'])
def get_products_for_order(order_id):
    order = Order.query.get_or_404(order_id)
    return products_schema.jsonify(order.products)

if __name__ == '__main__':
    app.run(debug=True)





