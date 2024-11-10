from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
db = SQLAlchemy(app)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    min_quantity = db.Column(db.Integer, nullable=False)
    unit = db.Column(db.String(20), nullable=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    quantity_change = db.Column(db.Integer, nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)
    notes = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    item = db.relationship('Item', backref=db.backref('transactions', lazy=True))

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    items = Item.query.all()
    low_stock_items = Item.query.filter(Item.quantity <= Item.min_quantity).all()
    return render_template('index.html', items=items, low_stock_items=low_stock_items)

@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        quantity = int(request.form['quantity'])
        min_quantity = int(request.form['min_quantity'])
        unit = request.form['unit']

        new_item = Item(
            name=name,
            category=category,
            quantity=quantity,
            min_quantity=min_quantity,
            unit=unit
        )
        db.session.add(new_item)
        db.session.commit()

        flash('Item added successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('add_item.html')

@app.route('/update_stock/<int:item_id>', methods=['GET', 'POST'])
def update_stock(item_id):
    item = Item.query.get_or_404(item_id)
    
    if request.method == 'POST':
        quantity_change = int(request.form['quantity_change'])
        transaction_type = request.form['transaction_type']
        notes = request.form['notes']

        transaction = Transaction(
            item_id=item.id,
            quantity_change=quantity_change,
            transaction_type=transaction_type,
            notes=notes
        )

        item.quantity += quantity_change
        item.last_updated = datetime.utcnow()
        
        db.session.add(transaction)
        db.session.commit()

        flash('Stock updated successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('update_stock.html', item=item)

@app.route('/transactions')
def transactions():
    transactions = Transaction.query.order_by(Transaction.timestamp.desc()).all()
    return render_template('transactions.html', transactions=transactions)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)