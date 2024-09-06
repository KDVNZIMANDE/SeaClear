from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.email = user_data['email']
        self.username = user_data['username']
        self.role = user_data['role']

class SeaClearApp:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'your_secret_key'  # Change this to a random secret key

        # MongoDB setup
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['seaclear_db']
        self.beaches_collection = self.db['beaches']
        self.users_collection = self.db['users']
        self.posts_collection = self.db['posts']

        # Flask-Login setup
        self.login_manager = LoginManager()
        self.login_manager.init_app(self.app)
        self.login_manager.login_view = 'login'

        self.setup_routes()
        self.setup_login_manager()

    def setup_routes(self):
        self.app.add_url_rule('/', 'home', self.home)
        self.app.add_url_rule('/about', 'about', self.about)
        self.app.add_url_rule('/educational', 'educational', self.educational)
        self.app.add_url_rule('/map', 'map', self.map)
        self.app.add_url_rule('/beach/<beach_id>', 'beach_detail', self.beach_detail, methods=['GET', 'POST'])
        self.app.add_url_rule('/post', 'post', self.post, methods=['POST'])
        self.app.add_url_rule('/like/<post_id>', 'like', self.like)
        self.app.add_url_rule('/admin', 'admin_dashboard', self.admin_dashboard)
        self.app.add_url_rule('/admin/approve/<post_id>', 'approve_post', self.approve_post)
        self.app.add_url_rule('/admin/deny/<post_id>', 'deny_post', self.deny_post)
        self.app.add_url_rule('/admin/delete_post/<post_id>', 'delete_post', self.delete_post)
        self.app.add_url_rule('/admin/edit_beach/<beach_id>', 'edit_beach', self.edit_beach, methods=['GET', 'POST'])
        self.app.add_url_rule('/admin/delete_beach/<beach_id>', 'delete_beach', self.delete_beach)
        self.app.add_url_rule('/admin/add_beach', 'add_beach', self.add_beach, methods=['GET', 'POST'])
        self.app.add_url_rule('/sign_up', 'sign_up', self.sign_up, methods=['GET', 'POST'])
        self.app.add_url_rule('/login', 'login', self.login, methods=['GET', 'POST'])
        self.app.add_url_rule('/logout', 'logout', self.logout)
        self.app.add_url_rule('/search', 'search', self.search)

    def setup_login_manager(self):
        @self.login_manager.user_loader
        def load_user(user_id):
            user_data = self.users_collection.find_one({'_id': ObjectId(user_id)})
            if user_data:
                return User(user_data)
            return None

    def home(self):
        beaches = list(self.beaches_collection.find())
        for beach in beaches:
            if 'Date' in beach and isinstance(beach['Date'], datetime):
                beach['Date'] = beach['Date'].strftime('%Y-%m-%d')
            elif 'Date' not in beach:
                beach['Date'] = 'N/A'
            
            if 'image' not in beach:
                beach['image'] = 'default_beach.jpg'
        
        return render_template('home.html', beaches=beaches)

    def about(self):
        return render_template('about.html')

    def educational(self):
        return render_template('educational.html')

    def map(self):
        return render_template('map.html')

    def beach_detail(self, beach_id):
        beach = self.beaches_collection.find_one({'_id': ObjectId(beach_id)})
        if not beach:
            flash('Beach not found.', 'danger')
            return redirect(url_for('home'))
        comments = self.posts_collection.find({'beach_id': ObjectId(beach_id), 'status': 'approved'})
        map_image = beach.get('map_image', 'default_beach.jpg')
        return render_template('beach_detail.html', beach=beach, comments=comments, map_image=map_image)

    @login_required
    def post(self):
        content = request.form['content']
        beach_id = request.form['beach_id']
        new_post = {
            'beach_id': ObjectId(beach_id),
            'user_id': current_user.id,
            'username': current_user.username,
            'timestamp': datetime.utcnow(), #should try find a different way to make timestamps
            'content': content,
            'status': 'pending',
            'likes': 0
        }
        self.posts_collection.insert_one(new_post)
        return redirect(url_for('beach_detail', beach_id=beach_id))

    @login_required
    def like(self, post_id):
        self.posts_collection.update_one({'_id': ObjectId(post_id)}, {'$inc': {'likes': 1}})
        post = self.posts_collection.find_one({'_id': ObjectId(post_id)})
        return redirect(url_for('beach_detail', beach_id=post['beach_id']))

    @login_required
    def admin_dashboard(self):
        if current_user.role != "admin":
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('home'))
        # Order Posts for the admin to view
        pipeline = [
            {
                "$addFields": {
                    "sort_order": {
                        "$switch": {
                            "branches": [
                                {"case": {"$eq": ["$status", "pending"]}, "then": 0},
                                {"case": {"$eq": ["$status", "denied"]}, "then": 1},
                            ],
                            "default": 2
                        }
                    }
                }
            },
            {"$sort": {"sort_order": 1}}
        ]
        posts = list(self.posts_collection.aggregate(pipeline))
        beaches = self.beaches_collection.find()
        return render_template('admin.html', posts=posts, beaches=beaches)

    @login_required
    def approve_post(self, post_id):
        if current_user.role != "admin":
            return redirect(url_for('home'))
        self.posts_collection.update_one({'_id': ObjectId(post_id)}, {'$set': {'status': 'approved'}})
        return redirect(url_for('admin_dashboard'))

    @login_required
    def deny_post(self, post_id):
        if current_user.role != "admin":
            return redirect(url_for('home'))
        self.posts_collection.update_one({'_id': ObjectId(post_id)}, {'$set': {'status': 'denied'}})
        return redirect(url_for('admin_dashboard'))

    @login_required
    def delete_post(self, post_id):
        try:
            result = self.posts_collection.delete_one({'_id': ObjectId(post_id)})
            if result.deleted_count > 0:
                flash('Post deleted successfully!', 'success')
            else:
                flash('Post not found!', 'danger')
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'danger')
        return redirect(url_for('admin_dashboard'))

    @login_required
    def edit_beach(self, beach_id):
        beach = self.beaches_collection.find_one({"_id": ObjectId(beach_id)})
        if request.method == 'POST':
            updated_data = {
                "name": request.form['name'],
                "location": request.form['location'],
                "date": request.form['date'],
                "entrocciticount": request.form['entrocciticount'],
                "grade": request.form['grade'],
                "temperature": request.form['temperature'],
                "wind_speed": request.form['wind_speed'],
                "wind_direction": request.form['wind_direction'],
                "status": request.form['status'],
            }
            if 'map_image' in request.files:
                map_image = request.files['map_image']
                if map_image.filename != '':
                    updated_data['map_image'] = map_image.filename
                    map_image.save(f"static/uploads/{map_image.filename}")
            self.beaches_collection.update_one({"_id": ObjectId(beach_id)}, {"$set": updated_data})
            flash('Beach updated successfully!', 'success')
            return redirect(url_for('edit_beach', beach_id=beach_id))
        return render_template('edit_beach.html', beach=beach)

    @login_required
    def delete_beach(self, beach_id):
        try:
            if not ObjectId.is_valid(beach_id):
                flash('Invalid beach ID.', 'danger')
                return redirect(url_for('admin_dashboard'))
            beach_id = ObjectId(beach_id)
            result = self.beaches_collection.delete_one({"_id": beach_id})
            if result.deleted_count > 0:
                flash('Beach deleted successfully!', 'success')
            else:
                flash('Beach not found.', 'danger')
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'danger')
        return redirect(url_for('admin_dashboard'))

    @login_required
    def add_beach(self):
        if request.method == 'POST':
            beach_data = {
                "name": request.form.get('name', ''),
                "location": request.form.get('location', ''),
                "date": request.form.get('date', ''),
                "entrocciticount": request.form.get('entrocciticount', ''),
                "grade": request.form.get('grade', ''),
                "temperature": request.form.get('temperature', ''),
                "wind_speed": request.form.get('wind_speed', ''),
                "wind_direction": request.form.get('wind_direction', ''),
                "status": request.form.get('status', ''),
                "map_image": 'default_beach.jpg'
            }
            self.beaches_collection.insert_one(beach_data)
            flash('Beach added successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        return render_template('add_beach.html')

    def sign_up(self):
        if request.method == 'POST':
            email = request.form.get('email')
            password1 = request.form.get('password1')
            password2 = request.form.get('password2')
            username = request.form.get('username')
            existing_user = self.users_collection.find_one({'email': email})
            if existing_user:
                flash('Email address already exists. Please choose another.', 'danger')
                return redirect(url_for('sign_up'))
            if password1 != password2:
                flash('Please ensure both passwords are the same.', 'danger')
                return redirect(url_for('sign_up'))
            hashed_password = generate_password_hash(password1, method='pbkdf2:sha256')
            new_user = {
                'email': email,
                'password': hashed_password,
                'username': username,
                'role': 'user'
            }
            self.users_collection.insert_one(new_user)
            flash('Sign-up successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        return render_template('sign_up.html')

    def login(self):
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            user = self.users_collection.find_one({'email': email})
            if user and check_password_hash(user['password'], password):
                user_obj = User(user)
                login_user(user_obj)
                flash('Logged in successfully.', 'success')
                return redirect(url_for('home'))
            else:
                flash('Invalid email or password', 'error')
        return render_template('login.html')

    @login_required
    def logout(self):
        logout_user()
        flash('Logged out successfully.', 'success')
        return redirect(url_for('home'))

    def search(self):   # needs to be adjusted for better search
        query = request.args.get('query', '')
        beaches = list(self.beaches_collection.find())
        return render_template('search_results.html', query=query, beaches=beaches)

    def run(self):
        self.app.run(debug=True)

if __name__ == '__main__':
    app = SeaClearApp()
    app.run()