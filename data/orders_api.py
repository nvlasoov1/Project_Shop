import flask
from flask import jsonify, request

from data import db_session
from data.orders import Orders


blueprint = flask.Blueprint(
    'orders_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/orders')
def get_orders():
    db_sess = db_session.create_session()
    orders = db_sess.query(Orders).all()
    return jsonify(
        {
            'products':
                [item.to_dict(only=('id', 'name', 'phone_number'))
                 for item in orders]
        }
    )

@blueprint.route('/api/orders/<int:order_id>', methods=['GET'])
def get_one_order(order_id):
    db_sess = db_session.create_session()
    orders = db_sess.query(Orders).get(order_id)
    if not orders:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'order': orders.to_dict(only=(
                'id', 'name', 'phone_number'))
        }
    )


@blueprint.route('/api/orders', methods=['POST'])
def create_orders():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['name', 'phone_number']):
        return jsonify({'error': 'Bad request'})
    db_sess = db_session.create_session()
    order = Orders(
        name=request.json['name'],
        phone_number=request.json['phone_number']
    )
    db_sess.add(order)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/products/<int:order_id>', methods=['DELETE'])
def delete_news(order_id):
    db_sess = db_session.create_session()
    order = db_sess.query(Orders).get(order_id)
    if not order:
        return jsonify({'error': 'Not found'})
    db_sess.delete(order)
    db_sess.commit()
    return jsonify({'success': 'OK'})