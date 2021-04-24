import flask
from flask import jsonify, request

from data import db_session
from data.products import Products


blueprint = flask.Blueprint(
    'products_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/products')
def get_products():
    db_sess = db_session.create_session()
    products = db_sess.query(Products).all()
    return jsonify(
        {
            'products':
                [item.to_dict(only=('id', 'name', 'price', 'created_date', 'user_id'))
                 for item in products]
        }
    )

@blueprint.route('/api/products/<int:product_id>', methods=['GET'])
def get_one_product(product_id):
    db_sess = db_session.create_session()
    products = db_sess.query(Products).get(product_id)
    if not products:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'product': products.to_dict(only=(
                'id', 'name', 'price', 'created_date', 'user_id'))
        }
    )


@blueprint.route('/api/products', methods=['POST'])
def create_news():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['name', 'price', 'user_id']):
        return jsonify({'error': 'Bad request'})
    db_sess = db_session.create_session()
    product = Products(
        name=request.json['name'],
        price=request.json['price'],
        user_id=request.json['user_id']
    )
    db_sess.add(product)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_news(product_id):
    db_sess = db_session.create_session()
    product = db_sess.query(Products).get(product_id)
    if not product:
        return jsonify({'error': 'Not found'})
    db_sess.delete(product)
    db_sess.commit()
    return jsonify({'success': 'OK'})