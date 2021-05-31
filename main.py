import sqlite3
import sys

from flask import Flask, render_template, url_for, request, session, make_response
from flask_sqlalchemy import SQLAlchemy

from werkzeug.utils import redirect
from werkzeug.security import generate_password_hash, check_password_hash

from flask_login import LoginManager, UserMixin

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from datetime import datetime

user_in = False

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'

db = SQLAlchemy(app)


#  Для авторизации


class Ads(db.Model):
    __tablename__ = 'ads sell'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(40), nullable=False)
    article_number = db.Column(db.String)
    text = db.Column(db.Text)
    location = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image = db.Column(db.BLOB)
    date = db.Column(db.DateTime, default=datetime.utcnow(), nullable=False)

    def __repr__(self):
        return "Ads %r" % self.id

    def set_image(self, image):
        """
        :param image: передаётся типом werkzeug.datastructures.FileStorage,
        тип возвращаемый при enctype="multipart/form-data" input type="file"
        :return:
        """
        try:
            self.image = image.read()
        except:
            print('Ошибка загрузки картинки')
            return None


class Accounts(db.Model, UserMixin):
    __tablename__ = 'accounts'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=False)
    password_hash = db.Column(db.String)
    name = db.Column(db.String, nullable=False)
    phone_number = db.Column(db.String(22), nullable=False)

    def __repr__(self):
        return "Login %r" % self.id

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)



@app.route('/')
@app.route('/home')
@app.route('/index')
def index():
    return render_template("index.html", user=user_in)


@app.route('/search_spare_parts')
def search_spare_parts():
    ads = Ads.query.order_by(Ads.date.desc()).all()
    return render_template("search_spare_parts.html", user=user_in, ads=ads)


@app.route('/search_spare_parts/<int:id>')
def ad_detail(id):
    ad = Ads.query.get(id)
    return render_template("ad_detail.html", user=user_in, ad=ad)


@app.route('/looking_spare_parts')
def looking_spare_parts():
    return render_template("looking_spare_parts.html", user=user_in)


@app.route('/create_ad_sell_spare_part', methods=['POST', 'GET'])
def create_ad_sell_spare_part():
    if request.method == "POST":
        title = request.form['ad_title']
        article_number = request.form['article_number']
        text = request.form['text']
        location = request.form['location']
        price = request.form['price']
        image = request.files['image_spare_part']

        ad_sell = Ads(title=title, article_number=article_number, text=text, location=location, price=price)
        ad_sell.set_image(image)
        try:
            db.session.add(ad_sell)
            db.session.commit()
            return redirect('/search_spare_parts')
        except:
            return "При добавлении объявления о продаже произошла ошибка"
    else:
        return render_template("create_ad_sell_spare_part.html", user=user_in)


@app.route('/profile/<int:id>/ad_delete')
def delete_ad_sell_spare_part(id):
    ad = Ads.query.get_or_404(id)

    try:
        db.session.delete(ad)
        db.session.commit()
        return redirect('/profile')
    except:
        return "При удалении объявления о продаже произошла ошибка"


@app.route('/create_ad_buy_spare_part', methods=['POST', 'GET'])
def create_ad_buy_spare_part():
    return render_template("create_ad_buy_spare_part.html", user=user_in)


@app.route('/authorization', methods=['POST', 'GET'])
def authorization():
    if request.method == 'POST':
        input_email = request.form['email']
        input_password = request.form['password']
        try:
            acc = db.session.query(Accounts).filter(Accounts.email == input_email).first()
            if acc.check_password(input_password):
                return redirect("/profile")
            else:
                return 'Неверный пароль'
        except:
            return "Ошибка авторизации"
    else:
        return render_template("authorization.html", user=user_in)


@app.route('/registration', methods=['POST', 'GET'])
def registration():
    if request.method == 'POST':
        name = request.form['name']
        phone_number = request.form['phone_number']
        email = request.form['email']
        password = request.form['password']
        account = Accounts(email=email, name=name, phone_number=phone_number)
        account.set_password(password)
        try:
            print(account.name, account.phone_number, account.email, account.password_hash)
            db.session.add(account)
            db.session.commit()
            return redirect("/authorization")
        except:
            return "Не удалось зарегистрироваться"
    else:
        return render_template("registration.html", user=user_in)


@app.route('/upload_image')
def upload_image():
    ad = db.session.query(Ads).get(2)
    img = ad.image
    return img

@app.route('/profile')
def profile():
    ads = Ads.query.order_by(Ads.date.desc()).all()
    return render_template("profile.html", user=user_in, ads=ads)


@app.route('/goodbye')
def user_out():
    global user_in
    user_in = False
    return redirect("/", code=302)


if __name__ == '__main__':
    app.run(debug=False)
