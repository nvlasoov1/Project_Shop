from os import abort, open
from flask import Flask, render_template, redirect
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from data import db_session, products_api, orders_api
from forms.user import RegisterForm, LoginForm
from data.users import User
from data.orders import Orders
from forms.product import ProductsForm
from data.products import Products
from cloudipsp import Api, Checkout
from forms.select import SelectForm
import oxr
from cut_image import resize_image


app = Flask(__name__)


app.config['SECRET_KEY'] = '165225asfagblp796796078asdafsaf412fa'


login_manager = LoginManager()
login_manager.init_app(app)


EXCHANGE_RATES = oxr.latest()
countries = EXCHANGE_RATES.keys()


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/', methods=['GET', 'POST'])
def start():
    form = SelectForm()
    current_rate = 1
    if form.validate_on_submit():
        current_country = form.cur.data
        current_rate = EXCHANGE_RATES[current_country]
    db_sess = db_session.create_session()
    items = db_sess.query(Products).all()
    for item in items:
        resize_image(item.image, item.image)
        db_sess.commit()
    return render_template("start.html", title='Каталог', data=items,
                           rate=current_rate, form=form)


@app.route('/about')
def about():
    return render_template("About.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            if form.user_type.data == 'Обычный пользователь' and user.type == 'Обычный пользователь':
                return redirect("/start_logged")
            elif form.user_type.data == 'Администратор' and user.type == 'Администратор':
                return redirect("/start_dev_logged")
        return render_template('Login.html',
                                message="Неправильный логин или пароль",
                                form=form)
    return render_template('Login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('Register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('Register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            phone_number=form.phone_number.data,
            email=form.email.data,
            type='Обычный пользователь'
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('Register.html', title='Регистрация', form=form)


@app.route('/start_logged', methods=['GET', 'POST'])
@login_required
def start_logged():
    form = SelectForm()
    current_country_usual = 'USD'
    current_rate_usual = 1
    if form.validate_on_submit():
        current_country_usual = form.cur.data
        current_rate_usual = EXCHANGE_RATES[current_country_usual]
    db_sess = db_session.create_session()
    items = db_sess.query(Products).all()
    return render_template("start_logged.html", title='Каталог', data=items, cur_country=current_country_usual,
                           rate=current_rate_usual, form=form)


@app.route('/about_logged')
@login_required
def about_logged():
    return render_template("About_logged.html", title='О нас')


@app.route('/about_dev_logged')
@login_required
def about_dev_logged():
    return render_template("About_dev_logged.html", title='О нас')


@app.route('/start_dev_logged', methods=['GET', 'POST'])
@login_required
def start_dev_logged():
    form = SelectForm()
    current_country_dev = 'USD'
    current_rate_dev = 1
    if form.validate_on_submit():
        current_country_dev = form.cur.data
        current_rate_dev = EXCHANGE_RATES[current_country_dev]
    db_sess = db_session.create_session()
    items = db_sess.query(Products).all()
    return render_template("start_dev_logged.html", title='Каталог', data=items, cur_country=current_country_dev,
                           rate=current_rate_dev, form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/adding', methods=['GET', 'POST'])
@login_required
def adding():
    form = ProductsForm()
    print(2)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        print(form.image.data)
        image_file = open(f'static/images/{str(form.image.data)}', "w")
        # image_file.write("Это текстовый файл")
        product = Products(name=form.name.data,
                               price=form.price.data,
                               image=image_file,
                               user_id=current_user.id)
        print(form.name.data, form.price.data)
        db_sess.products.append(product)
        db_sess.commit()
    return redirect('/adding')
    return render_template("Adding.html", title='Добавление товара', form=form)


@app.route('/buy/<int:id>:<string:cur_country>:<float:price>')
@login_required
def item_buy(id, cur_country, price):
    db_sess = db_session.create_session()
    item = db_sess.query(Products).filter(Products.id == id).first()
    print(1)
    order = Orders(name=item.name,
                   phone_number=current_user.phone_number)
    db_sess.add(order)
    price = round(price)
    api = Api(merchant_id=1396424,
            secret_key='test')
    checkout = Checkout(api=api)
    data = {
        "currency": cur_country,
        "amount": str(price) + "00"
    }
    db_sess.delete(item)
    db_sess.commit()
    url = checkout.url(data).get('checkout_url')
    return redirect(url)


@app.route('/orders', methods=['GET', 'POST'])
@login_required
def orders():
    db_sess = db_session.create_session()
    items = db_sess.query(Orders).all()
    return render_template("Orders.html", data=items)


@app.route('/orders_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def orders_delete(id):
    db_sess = db_session.create_session()
    orders = db_sess.query(Orders).filter(Orders.id == id).first()
    if orders:
        db_sess.delete(orders)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/orders')


@app.route('/products_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def products_delete(id):
    db_sess = db_session.create_session()
    products = db_sess.query(Products).filter(Products.id == id).first()
    if products:
        db_sess.delete(products)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/start_dev_logged')


if __name__ == '__main__':
    db_session.global_init("db/Users.db")
    app.register_blueprint(products_api.blueprint)
    app.register_blueprint(orders_api.blueprint)
    app.run(debug=True)