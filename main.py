# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import logging
from logging.handlers import RotatingFileHandler
from hashlib import sha256
from flask import Flask, render_template, request, redirect, json
import requests
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pay.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
shop_id = 5
secretKey = 'SecretKey01'
payway = 'advcash_rub'


class Paymets(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    currencys = db.Column(db.String(5), nullable= False)
    amounts = db.Column(db.String(100), nullable = False)
    descriptions = db.Column(db.Text, nullable=True)
    time = db.Column(db.DateTime, default = datetime.utcnow)

    def __repr__(self):
        return '<Article %r>' % self.id


def save_db(currency, amount, description):
    payments = Paymets(currencys = currency, amounts = amount, descriptions = description)
    db.session.add(payments)
    db.session.commit()



def hashing(data):
    dt = ""
    fl = 0
    for name in sorted(data.keys()):
        if fl == 0 and name != 'sign':
            dt = str(data[name])
            fl = 1
        elif fl == 1 and name != 'sign':
            dt = dt + ":" + str(data[name])
    dt = dt + secretKey
    return sha256(dt.encode('utf-8')).hexdigest()


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/', methods=['POST', 'GET'])
def index_post():
    amount = request.form.get('text').upper()
    currency = request.form.get('currency').upper()
    comment = request.form.get('comment').upper()
    if currency == '978':
        data1 = {
            "currency": currency,
            "amount": amount,
            "shop_id": shop_id,
            "shop_order_id": "101"}
        data1['sign'] = hashing(data1)
        save_db(currency, amount, comment)
        return render_template("pay.html", data1=data1)
    elif currency == '840':
        url = 'https://core.piastrix.com/bill/create'
        data2 = {
            "description": "Test Bill",
            "payer_currency": 643,
            "shop_amount": "23.15",
            "shop_currency": 643,
            "shop_id": "112",
            "shop_order_id": 4239,
            "sign": "ad7fbe8df102bc70e28deddba8b45bb3f4e6cafdaa69ad1ecc0e8b1d4e770575"
        }
        headers = {'Content-Type': 'application/json'}
        r = requests.post(url, data=json.dumps(data2), headers=headers)
        response = r.json()
        res = response["data"]
        save_db(currency, amount, comment)
        return redirect(res['url'], code=301)
    elif currency == '643':
        url = ' https://core.piastrix.com/invoice/create'
        data3 = {
            "currency": currency,
            "payway": payway,
            "amount": amount,
            "shop_id": shop_id,
            "shop_order_id": "101"
        }
        data3['sign'] = hashing(data3)
        headers = {'Content-Type': 'application/json'}
        r = requests.post(url, data=json.dumps(data3), headers=headers)
        response = r.json()
        res = response["data"]
        url = res["url"]
        method = res["method"]
        data3 = res["data"]
        save_db(currency, amount, comment)
        return render_template("invoice.html", method=method, url=url, data3=data3)


@app.route('/')
def foo():
    app.logger.warning('A warning occurred (%d apples)', 42)
    app.logger.error('An error occurred')
    app.logger.info('Info')
    return 'foo'


if __name__ == "__main__":
    handler = RotatingFileHandler('foo.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.run(debug=True)

