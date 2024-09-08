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

class Beach:
    def __init__(self, beach_data):
        self.id = str(beach_data['_id'])
        self.name = beach_data['name']
        self.location = beach_data['location']
        self.date = beach_data['date']
        self.description = beach_data['description']
        self.entrocciticount = beach_data['entrocciticount']
        self.grade = beach_data['grade']
        self.temperature = beach_data['temperature']
        self.wind_speed = beach_data['wind_speed']
        self.wind_direction = beach_data['wind_direction']
        self.status = beach_data['status']
        self.map_image = beach_data.get('map_image', 'default_beach.jpg')

    @classmethod
    def from_db(cls, beach_data):
        return cls(beach_data)

    def to_dict(self):
        return {
            'name': self.name,
            'location': self.location,
            'date': self.date,
            'description': self.description,
            'entrocciticount': self.entrocciticount,
            'grade': self.grade,
            'temperature': self.temperature,
            'wind_speed': self.wind_speed,
            'wind_direction': self.wind_direction,
            'status': self.status,
            'map_image': self.map_image
        }
    
    def get(self, attr, default=None):
        return getattr(self, attr, default)

class Post:
    def __init__(self, post_data):
        self.id = str(post_data['_id'])
        self.beach_id = str(post_data['beach_id'])
        self.user_id = post_data['user_id']
        self.username = post_data['username']
        self.timestamp = post_data['timestamp']
        self.content = post_data['content']
        self.status = post_data['status']
        self.likes = post_data['likes']
        self.beach = post_data['beach']

    @classmethod
    def from_db(cls, post_data):
        return cls(post_data)

    def to_dict(self):
        return {
            'beach_id': ObjectId(self.beach_id),
            'user_id': self.user_id,
            'username': self.username,
            'timestamp': self.timestamp,
            'content': self.content,
            'status': self.status,
            'likes': self.likes,
            'beach': self.beach
        }

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
        self.app.add_url_rule('/admin/approve_all_posts', 'approve_all_posts', self.approve_all_posts, methods=['POST'])
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
        beaches = [Beach.from_db(beach) for beach in self.beaches_collection.find()]
        return render_template('home.html', beaches=beaches)

    def about(self):
        return render_template('about.html')

    def educational(self):
        return render_template('educational.html')

    def map(self):
        return render_template('map.html')

    def beach_detail(self, beach_id):
        beach_data = self.beaches_collection.find_one({'_id': ObjectId(beach_id)})
        if not beach_data:
            flash('Beach not found.', 'danger')
            return redirect(url_for('home'))
        beach = Beach.from_db(beach_data)
        comments = [Post.from_db(post) for post in self.posts_collection.find({'beach_id': ObjectId(beach_id), 'status': 'approved'})]
        return render_template('beach_detail.html', beach=beach, comments=comments)

    @login_required
    def post(self):
        content = request.form['content']
        beach_id = request.form['beach_id']
        beach_name = request.form['beach_name']
        new_post = Post({
            '_id': ObjectId(),
            'beach_id': ObjectId(beach_id),
            'user_id': current_user.id,
            'username': current_user.username,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'content': content,
            'status': 'pending',
            'likes': 0,
            'beach': beach_name
        })
        self.posts_collection.insert_one(new_post.to_dict())
        return redirect(url_for('beach_detail', beach_id=beach_id))

    @login_required
    def like(self, post_id):
        self.posts_collection.update_one({'_id': ObjectId(post_id)}, {'$inc': {'likes': 1}})
        post_data = self.posts_collection.find_one({'_id': ObjectId(post_id)})
        post = Post.from_db(post_data)
        return redirect(url_for('beach_detail', beach_id=post.beach_id))

    @login_required
    def admin_dashboard(self):
        if current_user.role != "admin":
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('home'))
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
        posts = [Post.from_db(post) for post in self.posts_collection.aggregate(pipeline)]
        beaches = [Beach.from_db(beach) for beach in self.beaches_collection.find()]
        return render_template('admin.html', posts=posts, beaches=beaches)

    @login_required
    def approve_post(self, post_id):
        if current_user.role != "admin":
            return redirect(url_for('home'))
        self.posts_collection.update_one({'_id': ObjectId(post_id)}, {'$set': {'status': 'approved'}})
        return redirect(url_for('admin_dashboard'))
    

    @login_required
    def approve_all_posts(self):
        if current_user.role != "admin":
            flash('You do not have permission to perform this action.', 'danger')
            return redirect(url_for('admin_dashboard'))
        
        try:
            result = self.posts_collection.update_many(
                {'status': 'pending'},
                {'$set': {'status': 'approved'}}
            )
            
            if result.modified_count > 0:
                flash(f'{result.modified_count} pending posts approved successfully', 'success')
            else:
                flash('No pending posts to approve', 'info')
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'danger')
        
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
        beach_data = self.beaches_collection.find_one({"_id": ObjectId(beach_id)})
        beach = Beach.from_db(beach_data)
        if request.method == 'POST':
            updated_data = Beach({
                "_id": ObjectId(beach_id),
                "name": request.form['name'],
                "location": request.form['location'],
                "date": request.form['date'],
                "description": request.form['description'],
                "entrocciticount": request.form['entrocciticount'],
                "grade": request.form['grade'],
                "temperature": request.form['temperature'],
                "wind_speed": request.form['wind_speed'],
                "wind_direction": request.form['wind_direction'],
                "status": request.form['status'],
                "map_image": beach.map_image
            })
            if 'map_image' in request.files:
                map_image = request.files['map_image']
                if map_image.filename != '':
                    updated_data.map_image = map_image.filename
                    map_image.save(f"static/uploads/{map_image.filename}")
            self.beaches_collection.update_one({"_id": ObjectId(beach_id)}, {"$set": updated_data.to_dict()})
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
            new_beach = Beach({
                "_id": ObjectId(),
                "name": request.form.get('name', ''),
                "location": request.form.get('location', ''),
                "date": request.form.get('date', ''),
                "description": request.form.get('description', ''),
                "entrocciticount": request.form.get('entrocciticount', ''),
                "grade": request.form.get('grade', ''),
                "temperature": request.form.get('temperature', ''),
                "wind_speed": request.form.get('wind_speed', ''),
                "wind_direction": request.form.get('wind_direction', ''),
                "status": request.form.get('status', ''),
                "map_image": 'default_beach.jpg'
            })
            self.beaches_collection.insert_one(new_beach.to_dict())
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

    def search(self):
        query = request.args.get('query', '')
        beaches = [Beach.from_db(beach) for beach in self.beaches_collection.find(
            {"$or": [
                {"name": {"$regex": query, "$options": "i"}},
                {"location": {"$regex": query, "$options": "i"}}
            ]}
        )]
        return render_template('search_results.html', query=query, beaches=beaches)

    def run(self):
        self.app.run(debug=True)

if __name__ == '__main__':
    app = SeaClearApp()
    app.run()