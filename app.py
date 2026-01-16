import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'svara-secret-key-change-this'

# VERCEL DEPLOYMENT CONFIG
# Vercel is read-only. We must use /tmp for SQLite (NON-PERSISTENT) or external Postgres (PERSISTENT).
# For this demo, we use /tmp, meaning DB resets on redeploy.
if os.environ.get('VERCEL'):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/svara.db'
    app.config['UPLOAD_FOLDER'] = '/tmp'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///svara.db'
    app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')

app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Ensure upload directory exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False) # In production use hashed passwords

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.String(50), nullable=True)
    image_file = db.Column(db.String(100), nullable=False, default='default.jpg')
    instagram_url = db.Column(db.String(255), nullable=False)

# Helpers
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    recent_products = Product.query.limit(3).all()
    return render_template('index.html', products=recent_products)

@app.route('/products')
def products():
    products = Product.query.all()
    return render_template('products.html', products=products)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product_detail.html', product=product)

@app.route('/brand')
def brand():
    return render_template('brand.html')



# Admin Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.password == password: # Use hashing in real app
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin_dashboard():
    products = Product.query.all()
    return render_template('admin.html', products=products)

@app.route('/admin/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        instagram_url = request.form.get('instagram_url')
        
        image = request.files.get('image')
        image_filename = 'default.jpg'

        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_filename = filename

        new_product = Product(name=name, description=description, price=price, 
                              image_file=image_filename, instagram_url=instagram_url)
        db.session.add(new_product)
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    return render_template('add_product.html')

@app.route('/admin/edit_product/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    product = Product.query.get_or_404(id)
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.price = request.form.get('price')
        product.instagram_url = request.form.get('instagram_url')
        
        image = request.files.get('image')
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            product.image_file = filename
            
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    return render_template('edit_product.html', product=product)

@app.route('/admin/delete_product/<int:id>')
@login_required
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/sync_instagram')
@login_required
def sync_instagram():
    from instagram_sync import sync_instagram_posts
    success, message = sync_instagram_posts()
    if success:
        flash(message, 'success')
    else:
        flash(f'Error syncing: {message}', 'error')
    return redirect(url_for('admin_dashboard'))

# Setup Database
def create_initial_data():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            # Create default admin
            admin = User(username='admin', password='password')
            db.session.add(admin)
            db.session.commit()

if __name__ == '__main__':
    create_initial_data()
    app.run(debug=True)

# Vercel requires the app object to be named 'app' by default in the file specified in vercel.json
# We essentially expose it at module level, which is already done above `app = Flask(__name__)`
