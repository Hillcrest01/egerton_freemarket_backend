from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
CORS(app)

db = SQLAlchemy(app)
ma = Marshmallow(app)

if not os.path.exists('uploads'):
    os.makedirs('uploads')

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    contact_number = db.Column(db.String(15), nullable=False)
    image_filename = db.Column(db.String(100), nullable=False)

class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Product

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return products_schema.jsonify(products)

@app.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    product = Product.query.get(id)
    return product_schema.jsonify(product)

@app.route('/products', methods=['POST'])
def add_product():
    try:
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        contact_number = request.form['contact_number']
        if 'image' in request.files:
            image = request.files['image']
            image_filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
        else:
            image_filename = 'default.jpg'
        new_product = Product(name=name, description=description, price=price, contact_number=contact_number, image_filename=image_filename)
        db.session.add(new_product)
        db.session.commit()
        return jsonify({'message': 'Product added successfully', 'product': product_schema.dump(new_product)}), 201
    except Exception as e:
        return jsonify({'message': 'Failed to add product', 'error': str(e)}), 500

@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    try:
        product = Product.query.get(id)
        if not product:
            return jsonify({'message': 'Product not found'}), 404

        if 'name' in request.form:
            product.name = request.form['name']
        if 'description' in request.form:
            product.description = request.form['description']
        if 'price' in request.form:
            product.price = request.form['price']
        if 'contact_number' in request.form:
            product.contact_number = request.form['contact_number']
        if 'image' in request.files:
            image = request.files['image']
            image_filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
            product.image_filename = image_filename

        db.session.commit()
        return jsonify({'message': 'Product updated successfully', 'product': product_schema.dump(product)}), 200
    except Exception as e:
        return jsonify({'message': 'Failed to update product', 'error': str(e)}), 500


@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    try:
        product = Product.query.get(id)
        if not product:
            return jsonify({'message': 'Product not found'}), 404

        db.session.delete(product)
        db.session.commit()
        return jsonify({'message': 'Product deleted successfully'}), 200
    except Exception as e:
        return jsonify({'message': 'Failed to delete product', 'error': str(e)}), 500

@app.route('/uploads/<filename>')
def get_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
