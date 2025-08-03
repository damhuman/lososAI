import os
from flask import Flask, request, redirect, url_for, flash
from flask_admin import Admin, BaseView, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection
DATABASE_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Flask app setup
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

# Login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Simple user model for admin authentication
class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    if user_id == 'admin':
        return User(user_id)
    return None

# Custom admin index view with authentication
class SecureAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        
        # Get some statistics
        session = Session()
        try:
            # Count orders by status
            orders_stats = session.execute(
                text("SELECT status, COUNT(*) FROM orders GROUP BY status")
            ).fetchall()
            
            # Count products
            products_count = session.execute(
                text("SELECT COUNT(*) FROM products WHERE is_active = true")
            ).scalar()
            
            # Recent orders
            recent_orders = session.execute(
                text("""
                    SELECT o.id, o.contact_name, o.total_amount, o.status, o.created_at 
                    FROM orders o 
                    ORDER BY o.created_at DESC 
                    LIMIT 10
                """)
            ).fetchall()
            
            return self.render('admin/index.html', 
                             orders_stats=orders_stats,
                             products_count=products_count,
                             recent_orders=recent_orders)
        finally:
            session.close()

# Secure model views
class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated
    
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

# Custom views for different models
class OrderView(SecureModelView):
    column_list = ['id', 'contact_name', 'total_amount', 'status', 'delivery_date', 'created_at']
    column_searchable_list = ['contact_name', 'id']
    column_filters = ['status', 'delivery_date', 'created_at']
    column_editable_list = ['status']
    column_default_sort = ('created_at', True)
    
    def __init__(self, model, session, **kwargs):
        super(OrderView, self).__init__(model, session, **kwargs)

class ProductView(SecureModelView):
    column_list = ['id', 'name', 'category_id', 'price_per_kg', 'is_active', 'is_featured']
    column_searchable_list = ['name', 'id']
    column_filters = ['category_id', 'is_active', 'is_featured']
    column_editable_list = ['price_per_kg', 'is_active', 'is_featured']
    form_excluded_columns = ['order_items']

class UserView(SecureModelView):
    column_list = ['id', 'first_name', 'last_name', 'username', 'is_gold_client', 'is_blocked', 'created_at']
    column_searchable_list = ['first_name', 'last_name', 'username']
    column_filters = ['is_gold_client', 'is_blocked', 'language_code']
    column_editable_list = ['is_gold_client', 'is_blocked']

# Initialize admin
admin = Admin(app, name='Seafood Store Admin', 
              template_mode='bootstrap4',
              index_view=SecureAdminIndexView())

# Add model views (we'll import the models here)
try:
    # Import models from backend
    import sys
    sys.path.append('../backend')
    from app.db.models.order import Order, OrderItem
    from app.db.models.product import Category, Product, District, PromoCode
    from app.db.models.user import User as UserModel
    
    admin.add_view(OrderView(Order, Session(), name='Orders', category='Store'))
    admin.add_view(SecureModelView(OrderItem, Session(), name='Order Items', category='Store'))
    admin.add_view(ProductView(Product, Session(), name='Products', category='Catalog'))
    admin.add_view(SecureModelView(Category, Session(), name='Categories', category='Catalog'))
    admin.add_view(SecureModelView(District, Session(), name='Districts', category='Settings'))
    admin.add_view(SecureModelView(PromoCode, Session(), name='Promo Codes', category='Settings'))
    admin.add_view(UserView(UserModel, Session(), name='Users', category='Users'))
    
except ImportError as e:
    print(f"Warning: Could not import models: {e}")

# Login routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if (username == os.getenv('ADMIN_USERNAME') and 
            password == os.getenv('ADMIN_PASSWORD')):
            user = User('admin')
            login_user(user)
            return redirect(url_for('admin.index'))
        else:
            flash('Invalid credentials')
    
    return '''
    <form method="POST">
        <div style="max-width: 300px; margin: 100px auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
            <h2>Admin Login</h2>
            <p><input type="text" name="username" placeholder="Username" required style="width: 100%; padding: 10px; margin: 5px 0;"></p>
            <p><input type="password" name="password" placeholder="Password" required style="width: 100%; padding: 10px; margin: 5px 0;"></p>
            <p><input type="submit" value="Login" style="width: 100%; padding: 10px; background: #007bff; color: white; border: none; border-radius: 3px;"></p>
        </div>
    </form>
    '''

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)