from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'merchanttrade2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///merchants.db'
db = SQLAlchemy(app)

# Database Models
class Merchant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    shop_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    quantity = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    merchant_id = db.Column(db.Integer, db.ForeignKey('merchant.id'), nullable=False)
    merchant = db.relationship('Merchant', backref='stocks')
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)

# Routes
@app.route('/')
def home():
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    
    stocks = Stock.query
    
    if search:
        stocks = stocks.filter(Stock.title.contains(search))
    
    if category:
        stocks = stocks.filter_by(category=category)
    
    stocks = stocks.all()
    return render_template('index.html', stocks=stocks, search=search, category=category)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        merchant = Merchant(
            name=request.form['name'],
            shop_name=request.form['shop_name'],
            phone=request.form['phone'],
            location=request.form['location'],
            password=request.form['password']
        )
        db.session.add(merchant)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        merchant = Merchant.query.filter_by(
            phone=request.form['phone'],
            password=request.form['password']
        ).first()
        if merchant:
            session['merchant_id'] = merchant.id
            session['merchant_name'] = merchant.name
            return redirect(url_for('dashboard'))
        return render_template('login.html', error='Invalid credentials!')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'merchant_id' not in session:
        return redirect(url_for('login'))
    stocks = Stock.query.filter_by(merchant_id=session['merchant_id']).all()
    return render_template('dashboard.html', stocks=stocks)

@app.route('/post_stock', methods=['GET', 'POST'])
def post_stock():
    if 'merchant_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        stock = Stock(
            title=request.form['title'],
            description=request.form['description'],
            quantity=request.form['quantity'],
            price=float(request.form['price']),
            category=request.form['category'],
            merchant_id=session['merchant_id']
        )
        db.session.add(stock)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('post_stock.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))
@app.route('/delete_stock/<int:stock_id>')
def delete_stock(stock_id):
    if 'merchant_id' not in session:
        return redirect(url_for('login'))
    stock = Stock.query.get(stock_id)
    if stock and stock.merchant_id == session['merchant_id']:
        db.session.delete(stock)
        db.session.commit()
    return redirect(url_for('dashboard'))
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)