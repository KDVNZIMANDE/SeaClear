from datetime import datetime
from io import BytesIO

import requests
from apscheduler.schedulers.background import BackgroundScheduler
from bson.objectid import ObjectId
from flask import (Flask, Response, flash, jsonify, redirect, render_template,
                   request, send_file, session, url_for)
from flask_login import (LoginManager, UserMixin, current_user, login_required,
                         login_user, logout_user)
from gridfs import GridFS
from pymongo import MongoClient
from werkzeug.security import check_password_hash, generate_password_hash


class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.email = user_data['email']
        self.username = user_data['username']
        self.role = user_data['role']
        self.favorites = user_data.get('favorites', [])

class Beach:
    def __init__(self, beach_data):
        self.id = str(beach_data['_id'])
        self.name = beach_data['name']
        self.location = beach_data.get('location', 'Unknown Location')  #TO-DO maybe change all to use get (this is a form of error handling)
        self.location_code = beach_data.get('location_code', '2a4a3941719942132f9ed4f71b5feadec34a454fbf3b03789def2d719b4b2e92')
        self.longitude = beach_data.get('longitude', None)
        self.latitude = beach_data.get('latitude', None)
        self.date = beach_data['date']
        self.description = beach_data['description']
        self.enterococcicount = beach_data.get('enterococcicount')
        self.grade = beach_data['grade']
        self.temperature = beach_data['temperature']
        self.wind_speed = beach_data['wind_speed']
        self.weather_description = beach_data.get('weather_description',None)
        self.status = beach_data['status']
        self.map_image = beach_data.get('map_image', 'default_beach.jpg')
        self.has_amenities = beach_data.get('has_amenities', False)
        self.amenities = beach_data.get('amenities', [])
        self.safety_rating = beach_data.get('safety_rating', 0)
        self.clean_rating = beach_data.get('clean_rating', 0)
        self.num_ratings = beach_data.get('num_ratings', 0)
        
    
    @classmethod
    def from_db(cls, beach_data):
        return cls(beach_data)

    def to_dict(self):
        return {
            'name': self.name,
            'location': self.location,
            'location_code': self.location_code,
            'longitude': self.longitude,
            'latitude': self.latitude,
            'date': self.date,
            'description': self.description,
            'enterococcicount': self.enterococcicount,
            'grade': self.grade,
            'temperature': self.temperature,
            'wind_speed': self.wind_speed,
            'weather_description': self.weather_description,
            'status': self.status,
            'map_image': self.map_image,
            'has_amenities': self.has_amenities,
            'amenities': self.amenities,
            'safety_rating' :self.safety_rating,
            'clean_rating' :self.clean_rating,
            'num_ratings' : self.num_ratings
        }
    
    def get(self, attr, default=None):
        return getattr(self, attr, default)
    
    def add_amenity(self, amenity):
        if amenity not in self.amenities:
            self.amenities.append(amenity)
            self.has_amenities = True

    def remove_amenity(self, amenity):
        if amenity in self.amenities:
            self.amenities.remove(amenity)
            if not self.amenities:
                self.has_amenities = False

    def set_amenities(self, amenities):
        self.amenities = list(set(amenities))  # Remove duplicates
        self.has_amenities = bool(self.amenities)

    def get_amenities(self):
        return self.amenities
    
    def get_amenity_icon(self, amenity):
        # Define a mapping of amenities to icon classes
        icon_map = {
            'Restrooms': 'fa fa-restroom',
            'Parking': 'fa fa-parking',
            'Showers': 'fa fa-shower',
            'Lifeguard': 'fa fa-life-ring',
            'Picnic Area': 'fa fa-table',
            'Trash Cans': 'fa fa-trash',
            'Wheelchair Access': 'fa fa-wheelchair',
            'Swimming pool': 'fa fa-swimmer',
            'Changing Rooms': 'fa fa-tshirt',
            'First Aid': 'fa fa-plus',
            'Wi-Fi': 'fa fa-wifi',
            'ATM': 'fa fa-credit-card',
            'Boat Rental': 'fa fa-anchor',
            'Bike Rental': 'fa fa-bicycle',
            'Fishing': 'fa fa-fish',
            'Surfing': 'fa fa-surfing',
            'Beach Volleyball': 'fa fa-volleyball-ball',
            'Playground': 'fa fa-child',
            'Event Space': 'fa fa-calendar',
            'Public Transport': 'fa fa-bus',
            'Taxi': 'fa fa-taxi',
            'Emergency Services': 'fa fa-ambulance',
            'Barbecue': 'fa fa-fire',
            'Dog Friendly': 'fa fa-dog',
            'Sunset Viewing': 'fa fa-sun',
            'Observation Deck': 'fa fa-binoculars'
        }

        return icon_map.get(amenity, '')  # Default icon if not found

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
        self.replies = post_data.get('replies', [])

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
    
class Reply:
    def __init__(self, reply_data):
        self.user_id = reply_data['user_id']
        self.username = reply_data['username']
        self.timestamp = reply_data['timestamp']
        self.content = reply_data['content']
        self.likes = reply_data.get('likes', 0)

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'username': self.username,
            'timestamp': self.timestamp,
            'content': self.content,
            'likes': self.likes
        }
    
class Report:
    def __init__(self, report_data):
        self.id = str(report_data['_id'])
        self.beach = report_data['beach']
        self.date = report_data['date']
        self.enterococcicount = report_data['enterococcicount']

    @classmethod
    def from_db(cls, report_data):
        return cls(report_data)
    
    def to_dict(self):
        return{
            'beach' : self.beach,
            'date' : self.date,
            'enterococcicount' : self.enterococcicount
        }
        
class CommunityReport:
    def __init__(self, community_report_data):
        self.id = str(community_report_data['_id'])
        self.problem_type = community_report_data['problem_type']
        self.problem_description = community_report_data.get['problem_description']
        self.user_id = community_report_data['user_id']
        self.beach = community_report_data['beach']
        self.date= community_report_data['date']
    @classmethod
    def from_db(cls, community_report_data):
        return cls(community_report_data)
    
    def to_dict(self):
        return {
            'problem_type': self.problem_type,
            'problem_description': self.problem_description,
            'user_id': self.user_id,
            'beach': self.beach,
            'date' : self.date
            
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
        self.reports_collection = self.db['reports']
        self.community_reports_collection = self.db['community_reports']
        self.fs = GridFS(self.db)   #for images

        # Flask-Login setup
        self.login_manager = LoginManager()
        self.login_manager.init_app(self.app)
        self.login_manager.login_view = 'login'

        # Initialize APScheduler
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(func=self.update_weather_data, trigger="interval", minutes=30)
        self.scheduler.start()

        self.setup_routes()
        self.setup_login_manager()

    def setup_routes(self):
        self.app.add_url_rule('/', 'home', self.home)
        self.app.add_url_rule('/about', 'about', self.about)
        self.app.add_url_rule('/educational', 'educational', self.educational)
        self.app.add_url_rule('/map', 'map', self.map)
        self.app.add_url_rule('/all_beaches', 'all_beaches', self.all_beaches)
        self.app.add_url_rule('/beach/<beach_id>', 'beach_detail', self.beach_detail, methods=['GET', 'POST'])
        self.app.add_url_rule('/post', 'post', self.post, methods=['POST'])
        self.app.add_url_rule('/add_reply', 'add_reply', self.add_reply, methods=['POST'])
        self.app.add_url_rule('/like/<post_id>', 'like', self.like)
        self.app.add_url_rule('/like_reply/<post_id>/<reply_index>', 'like_reply', self.like_reply)
        self.app.add_url_rule('/favorites/<beach_id>/<view>', 'favorites', self.favorites)
        self.app.add_url_rule('/admin', 'admin_dashboard', self.admin_dashboard)
        self.app.add_url_rule('/admin/manage-posts','manage_posts', self.manage_posts)
        self.app.add_url_rule('/admin/manage-beaches','manage_beaches', self.manage_beaches)
        self.app.add_url_rule('/admin/manage-reports','manage_reports', self.manage_reports)
        self.app.add_url_rule('/admin/approve/<post_id>', 'approve_post', self.approve_post)
        self.app.add_url_rule('/admin/approve_all_posts', 'approve_all_posts', self.approve_all_posts, methods=['POST'])
        self.app.add_url_rule('/admin/deny/<post_id>', 'deny_post', self.deny_post)
        self.app.add_url_rule('/admin/delete_post/<post_id>', 'delete_post', self.delete_post)
        self.app.add_url_rule('/admin/edit_beach/<beach_id>', 'edit_beach', self.edit_beach, methods=['GET', 'POST'])
        self.app.add_url_rule('/admin/delete_beach/<beach_id>', 'delete_beach', self.delete_beach)
        self.app.add_url_rule('/admin/add_beach', 'add_beach', self.add_beach, methods=['GET', 'POST'])
        self.app.add_url_rule('/admin/edit_report/<report_id>', 'edit_report', self.edit_report, methods=['GET', 'POST'])
        self.app.add_url_rule('/admin/delete_report/<report_id>', 'delete_report', self.delete_report)
        self.app.add_url_rule('/admin/add_report', 'add_report', self.add_report, methods=['GET', 'POST'])
        self.app.add_url_rule('/sign_up', 'sign_up', self.sign_up, methods=['GET', 'POST'])
        self.app.add_url_rule('/login', 'login', self.login, methods=['GET', 'POST'])
        self.app.add_url_rule('/logout', 'logout', self.logout)
        self.app.add_url_rule('/search', 'search', self.search)
        self.app.add_url_rule('/images/<file_id>', 'get_image', self.get_image)  
        self.app.add_url_rule('/news', 'news_page', self.news_page)  
        self.app.add_url_rule('/impact', 'impact_page', self.impact_page)
        self.app.add_url_rule('/quiz', 'impact_quiz', self.impact_quiz)
        self.app.add_url_rule('/community_report','community_report', self.community_report, methods=['GET', 'POST'])
        
        self.app.add_url_rule('/get_ratings/<beach_id>', 'get_ratings', self.get_ratings, methods=['GET'])
        self.app.add_url_rule('/rate_beach/<beach_id>', 'rate_beach', self.rate_beach, methods=['GET'])
        self.app.add_url_rule('/submit_rating', 'submit_rating', self.submit_rating, methods=['POST'])
        

    def impact_quiz(self):
        return render_template('impact_quiz.html')
    
    def news_page(self):
        return render_template('news.html')
    
    def impact_page(self):
        return render_template('impact.html')
     
    def community_report(self):
        return render_template('add_community_report.html')

    def setup_login_manager(self):
        @self.login_manager.user_loader
        def load_user(user_id):
            user_data = self.users_collection.find_one({'_id': ObjectId(user_id)})
            if user_data:
                return User(user_data)
            return None

    @login_required
    def rate_beach(self,beach_id):
        beach = self.beaches_collection.find_one({'_id': ObjectId(beach_id)})
        return render_template('rate_beach.html', beach=beach, beach_id=beach_id)

    def submit_rating(self):
        try:
            # Get data from the request
            beach_id = request.form.get('beach_id')
            if not ObjectId.is_valid(beach_id):
                return jsonify({'success': False, 'error': 'Invalid beach ID format'}), 400
            
            safety_rating = float(request.form['safety_rating'])
            clean_rating = float(request.form['clean_rating'])

            # Validate ratings
            if not (1 <= safety_rating <= 5) or not (1 <= clean_rating <= 5):
                return jsonify({'success': False, 'error': 'Ratings must be between 1 and 5'}), 400

            # Check if the beach exists in the database
            beach = self.beaches_collection.find_one({"_id": ObjectId(beach_id)})
            if beach:
                # Default values if num_ratings does not exist
                num_ratings = beach.get('num_ratings', 0)
                current_safety_rating = beach.get('safety_rating', 0)
                current_clean_rating = beach.get('clean_rating', 0)

                # Calculate new average ratings
                new_safety_rating = (current_safety_rating * num_ratings + safety_rating) / (num_ratings + 1)
                new_clean_rating = (current_clean_rating * num_ratings + clean_rating) / (num_ratings + 1)
                new_num_ratings = num_ratings + 1

                # Update ratings in the database
                self.beaches_collection.update_one(
                    {"_id": ObjectId(beach_id)},
                    {"$set": {
                        'safety_rating': new_safety_rating,
                        'clean_rating': new_clean_rating,
                        'num_ratings': new_num_ratings
                    }}
                )
                return jsonify({'success': True, 'message': 'Rating updated successfully'})
            else:
                return jsonify({'success': False, 'error': 'Beach not found'}), 404
        except ValueError:
            return jsonify({'success': False, 'error': 'Invalid rating values'}), 400
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500


    def get_ratings(self, beach_id):
        beach = self.beaches_collection.find_one({"_id": ObjectId(beach_id)})
        if beach:
            return jsonify({
                'safety_rating': beach['safety_rating'],
                'clean_rating': beach['clean_rating']
            })
        else:
            return jsonify({'error': 'Beach not found'}), 404

    def sort_reports_by_date(self, reports):
        # Sort reports by date in descending order (most recent first)
        sorted_reports = sorted(reports, key=lambda report: datetime.strptime(report['date'], '%Y-%m-%d'), reverse=True)
        return sorted_reports

    def update_weather_data(self):
        # """Fetch and update the weather data for all beaches in the database."""
        weather_api_key = "e4f0bddc1fc2079118ed71df7a9fa6d7"
        beaches = self.beaches_collection.find()

        for beach in beaches:
            latitude = beach.get('latitude')
            longitude = beach.get('longitude')
            if latitude and longitude:
                weather_url = f"http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&units=metric&appid={weather_api_key}"

                weather_data = requests.get(weather_url).json()
                if weather_data:
                    temperature = weather_data['main']['temp']
                    wind_speed = weather_data['wind']['speed']
                    weather_description = weather_data['weather'][0]['description']

                    # Update the beach document in MongoDB
                    self.beaches_collection.update_one(
                        {'_id': beach['_id']},
                        {
                            '$set': {
                                'temperature': temperature,
                                'wind_speed': wind_speed,
                                'weather_description': weather_description,
                            }
                        }
                    )

    def home(self):
    
        beaches = [Beach.from_db(beach) for beach in self.beaches_collection.find()]
    # Updated news_items
        news_items = [
        {
            'title': 'Coastal Water Quality',
            'content': 'Learn about the quality of coastal water and its importance.',
            'image': 'beach_red.jfif',
            'link': 'https://www.capetown.gov.za/Explore%20and%20enjoy/nature-and-outdoors/our-precious-biodiversity/coastal-water-quality'
        },
        {
            'title': 'Waterborne Diseases',
            'content': 'Explore the impact of waterborne diseases on health.',
            'image': 'beach_red.jfif',
            'link': 'https://www.niehs.nih.gov/research/programs/climatechange/health_impacts/waterborne_diseases'
           
        },
        {
            'title': '‘Red Flag’ Beaches',
            'content': 'Discover which Cape Town beaches have chronic water quality problems.',
            'image': 'beach_red.jfif',
            'link': 'https://www.thesouthafrican.com/news/these-popular-cape-town-beaches-have-chronic-water-quality-problems-breaking-12-december-2023/'
        },
        {
            'title': 'Swimming Related Illnesses',
            'content': 'Understand the risks of swimming-related illnesses.',
            'image': 'image1.jfif',
            'link': 'https://time.com/5631608/swimming-illness-risks/'
        },
        {
           'title': 'Coastal Concerns',
            'content': 'Read about bacterial infections and the need for effective water quality flags.',
            'image': 'bacteria.jfif',
            'link': 'https://www.dailymaverick.co.za/article/2024-01-23-after-bacterial-infections-strand-beachgoers-call-for-effective-city-of-cape-town-water-quality-flag-system/'  
        },
        {
            'title': 'Dangerously High Pollution Levels',
            'content': 'Latest data on pollution levels in Cape Town\'s vleis.',
            'image': 'vleis.jfif',
            'link': 'https://www.dailymaverick.co.za/article/2021-11-08-latest-data-reveals-dangerously-high-pollution-levels-in-cape-towns-vleis/'
        },
        {
            'title': 'Code Red on Water Quality',
            'content': 'It\'s code red on the water quality of beaches around Cape Town.',
            'image': 'codered.jfif',
            'link': 'https://www.dailymaverick.co.za/article/2023-12-04-its-code-red-on-the-water-quality-of-beaches-around-cape-town-ahead-of-peak-holiday-season/'
        },
        {
            'title': 'Water Quality Assurance',
            'content': 'Assurance through testing and quality control measures.',
            'image': 'quality.jfif',
            'link': 'https://resource.capetown.gov.za/documentcentre/Documents/Graphics%20and%20educational%20material/Water%20quality%20-%20assurance%20through%20testing%20.pdf.pdf'
        },
        {
            'title': 'Concerns Over Water Quality',
            'content': 'Concerns over water quality and safety at popular Strand Beach.',
            'image': 'illness.jfif',
            'link': 'https://www.iol.co.za/sunday-tribune/travel/surge-in-illnesses-sparks-concerns-over-water-quality-and-safety-at-popular-strand-beach-f7c7e332-7bb1-46f7-935a-0320f1a5b321'
        }
    ]
        return render_template('home.html', beaches=beaches, news_items=news_items)


    

    def about(self):
        return render_template('about.html')

    def educational(self):
        return render_template('educational.html')

    def map(self):
        beaches = [Beach.from_db(beach) for beach in self.beaches_collection.find()]
        return render_template('map.html', beaches=beaches)


    def all_beaches(self):
        beaches = [Beach.from_db(beach) for beach in self.beaches_collection.find()]
        favorite_beaches = []

        if current_user.is_authenticated:
            # Fetch each favorite beach from the user's favorites
            for favorite in current_user.favorites:
                beach_data = self.beaches_collection.find_one({'_id': ObjectId(favorite)})
                if beach_data:
                    beach_data['id'] = str(beach_data['_id'])
                    favorite_beaches.append(beach_data)

        return render_template('all_beaches.html', beaches=beaches, favorite_beaches=favorite_beaches)

    def get_amenity_icon(self, amenity):
        # Define a mapping of amenities to icon classes
        icon_map = {
            'Restroom': 'fa fa-restroom',  # Example Font Awesome class
            'Parking': 'fa fa-parking',
            'Food': 'fa fa-utensils',
            # Add other amenities and their icons
        }
        return icon_map.get(amenity, 'fa fa-question')  # Default icon if not found

    def beach_detail(self, beach_id):
        beach_data = self.beaches_collection.find_one({'_id': ObjectId(beach_id)})
        weather_api_key = "e4f0bddc1fc2079118ed71df7a9fa6d7"
        latitude = beach_data.get('latitude')
        longitude = beach_data.get('longitude')
        
        if not beach_data:
            flash('Beach not found.', 'danger')
            return redirect(url_for('home'))
        
        # Fetch weather data
        
        weather_url = f"http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&units=metric&appid={weather_api_key}"
        weather_data = None
        try:
            weather_data = requests.get(weather_url).json()
        except:
            weather_data = {"main": {"temp": "N/A"}, "weather": [{"description": "N/A"}], "wind": {"speed": "N/A"}}

        reports = self.reports_collection.find({'beach': beach_data.get('name')})
        reports = self.sort_reports_by_date(reports)
        report_list = [{'date': report.get('date'),'enterococcicount': report.get('enterococcicount')} for report in reports]
        beach = Beach.from_db(beach_data)
        comments = [Post.from_db(post) for post in self.posts_collection.find({'beach_id': ObjectId(beach_id), 'status': 'approved'})]
        return render_template('beach_detail.html', beach=beach, comments=comments, weather=weather_data, reports=report_list) 

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
    def add_reply(self):
        content = request.form['content']
        post_id = request.form['post_id']
        post = self.posts_collection.find_one({'_id': ObjectId(post_id)})
        
        if not post:
            flash('Post not found.', 'danger')
            return redirect(url_for('home'))

        new_reply = Reply({
            'user_id': current_user.id,
            'username': current_user.username,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'content': content,
            'likes': 0
        })

        self.posts_collection.update_one(
            {'_id': ObjectId(post_id)},
            {'$push': {'replies': new_reply.to_dict()}}
        )

        return redirect(url_for('beach_detail', beach_id=post['beach_id']))

    @login_required
    def like(self, post_id):
        user_id = current_user.id
        post = self.posts_collection.find_one({'_id': ObjectId(post_id)})
        # Check if user has already liked the post
        if user_id in post.get('liked_users', []):
            # Handle case where user has already liked the post
            self.posts_collection.update_one(
            {'_id': ObjectId(post_id)},{'$inc': {'likes': -1}, '$pull': {'liked_users': user_id}}
            )
            return redirect(url_for('beach_detail', beach_id=post.get('beach_id')))
        
        # Update the post with a new like
        self.posts_collection.update_one(
            {'_id': ObjectId(post_id)}, {'$inc': {'likes': 1},'$push': {'liked_users': user_id} })
        
        post_data = self.posts_collection.find_one({'_id': ObjectId(post_id)})
        post = Post.from_db(post_data)
        return redirect(url_for('beach_detail', beach_id=post.beach_id))
    
    @login_required
    def like_reply(self, post_id, reply_index):
        user_id = current_user.id
        reply_index = int(reply_index)
        post = self.posts_collection.find_one({'_id': ObjectId(post_id)})

        if not post:
            flash('Post not found.', 'danger')
            return redirect(url_for('home'))

        replies = post.get('replies', [])
        if reply_index >= len(replies):
            flash('Reply not found.', 'danger')
            return redirect(url_for('beach_detail', beach_id=post['beach_id']))

        reply = replies[reply_index]
        
        if user_id in reply.get('liked_users', []):
            # Unlike the reply
            self.posts_collection.update_one(
                {'_id': ObjectId(post_id)},
                {'$inc': {'replies.$.likes': -1}, '$pull': {'replies.$.liked_users': user_id}}
            )
        else:
            # Like the reply
            self.posts_collection.update_one(
                {'_id': ObjectId(post_id)},
                {'$inc': {f'replies.{reply_index}.likes': 1}}
            )

        return redirect(url_for('beach_detail', beach_id=post['beach_id']))
    
    @login_required
    def favorites(self, beach_id, view):
        user_id = current_user.id
        beach = self.beaches_collection.find_one({"_id": ObjectId(beach_id)})
        
        # Check if the beach is already in the user's favorites
        if beach_id in current_user.favorites:
            # Remove from favorites
            self.users_collection.update_one(
                {'_id': ObjectId(user_id)},
                {'$pull': {'favorites': beach_id}}
            )
            flash(f'Removed {beach["name"]} from your favorites.', 'danger')

        else:
            # Add to favorites
            self.users_collection.update_one(
                {'_id': ObjectId(user_id)},
                {'$push': {'favorites': beach_id}}
            )
            flash(f'Added {beach["name"]} to your favorites!', 'success')

        if view == "beaches":
            return redirect(url_for('all_beaches'))
        elif view == "map":
            return redirect(url_for('map'))
        elif view == "search":
            return redirect(url_for('search'))
 
        return redirect(url_for('beach_detail', beach_id=beach_id))

    @login_required
    def admin_dashboard(self):
        if current_user.role != "admin":
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('home'))
        return render_template('admin.html')
    
    @login_required
    def manage_posts(self):
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
        return render_template('manage_posts.html', posts=posts)
    
    @login_required
    def manage_beaches(self):
        if current_user.role != "admin":
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('home'))
        beaches = [Beach.from_db(beach) for beach in self.beaches_collection.find()]
        return render_template('manage_beaches.html', beaches=beaches)
    
    def manage_reports(self):
        if current_user.role != "admin":
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('home'))
        reports = [Report.from_db(report) for report in self.reports_collection.find()]
        return render_template('manage_reports.html', reports=reports)

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
        # Fetch the existing beach data
        beach_data = self.beaches_collection.find_one({"_id": ObjectId(beach_id)})
        beach = Beach.from_db(beach_data)

        if request.method == 'POST':
            # Create updated beach data from the form
            updated_data = Beach({
                "_id": ObjectId(beach_id),
                "name": request.form['name'],
                "location": request.form['location'],
                "longitude": float(request.form['longitude']),
                "latitude": float(request.form['latitude']),
                "date": request.form['date'],
                "description": request.form['description'],
                "enterococcicount": request.form['enterococcicount'],
                "grade": request.form['grade'],
                "temperature": request.form['temperature'],
                "wind_speed": request.form['wind_speed'],
                "weather_description": request.form['weather_description'],
                "status": request.form['status'],
                "map_image": beach.map_image,  # Use existing image unless updated
                "has_amenities": request.form.get('has_amenities') == 'on',
                "amenities": request.form.getlist('amenities[]')
            })

            # Check if a new image is uploaded
            if 'map_image' in request.files:
                map_image = request.files['map_image']
                if map_image.filename != '':
                    # Delete the old image from GridFS if it exists
                    if beach.map_image and ObjectId.is_valid(beach.map_image):
                        self.fs.delete(ObjectId(beach.map_image))

                    # Save the new image to GridFS
                    map_image_id = self.fs.put(map_image, filename=map_image.filename)
                    updated_data.map_image = str(map_image_id)  # Store GridFS file ID

            try:
                # Update the beach document in MongoDB
                self.beaches_collection.update_one(
                    {"_id": ObjectId(beach_id)}, 
                    {"$set": updated_data.to_dict()}
                )
                flash('Beach updated successfully!', 'success')
            except Exception as e:
                flash(f'Error updating beach: {str(e)}', 'error')
            
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
            # Create new beach data from the form
            new_beach = Beach({
                "_id": ObjectId(),
                "name": request.form['name'],
                "location": request.form['location'],
                "latitude": float(request.form.get('latitude', 0)),
                "longitude": float(request.form.get('longitude', 0)),
                "date": request.form['date'],
                "description": request.form['description'],
                "enterococcicount": request.form['enterococcicount'],
                "grade": request.form['grade'],
                "temperature": request.form['temperature'],
                "wind_speed": request.form['wind_speed'],
                "weather_description": request.form['weather_description'],
                "status": request.form['status'],
                "map_image": None  # Initialize with no image
            })

            # Handle image upload
            if 'map_image' in request.files:
                map_image = request.files['map_image']
                if map_image.filename != '':
                    try:
                        # Save the image to GridFS
                        map_image_id = self.fs.put(map_image, filename=map_image.filename)
                        new_beach.map_image = str(map_image_id)  # Store GridFS file ID
                    except Exception as e:
                        flash(f'Error uploading image: {str(e)}', 'error')

            # Handle amenities
            has_amenities = request.form.get('has_amenities') == 'on'
            new_beach.has_amenities = has_amenities
            new_beach.amenities = request.form.getlist('amenities[]') if has_amenities else []

            try:
                # Insert the new beach document into MongoDB
                self.beaches_collection.insert_one(new_beach.to_dict())
                flash('Beach added successfully!', 'success')
                return redirect(url_for('admin_dashboard'))
            except Exception as e:
                flash(f'Error adding beach: {str(e)}', 'error')

        return render_template('add_beach.html')

    @login_required
    def edit_report(self, report_id):
        # Fetch the existing beach data
        report_data = self.reports_collection.find_one({"_id": ObjectId(report_id)})
        report = Report.from_db(report_data)

        if request.method == 'POST':
            # Create updated report data from the form
            updated_data = Report({
                "_id": ObjectId(report_id),
                "beach": request.form['beach'],
                "date": request.form['date'],
                "enterococcicount": request.form['enterococcicount']

            })

            # Update the beach document in MongoDB
            self.reports_collection.update_one({"_id": ObjectId(report_id)}, {"$set": updated_data.to_dict()})

            flash('Report updated successfully!', 'success')
            return redirect(url_for('admin_dashboard'))

        return render_template('edit_report.html', report=report)
    
    @login_required
    def delete_report(self, report_id):
        try:
            if not ObjectId.is_valid(report_id):
                flash('Invalid report ID.', 'danger')
                return redirect(url_for('admin_dashboard'))
            report_id = ObjectId(report_id)
            result = self.reports_collection.delete_one({"_id": report_id})
            if result.deleted_count > 0:
                flash('Report deleted successfully!', 'success')
            else:
                flash('Report not found.', 'danger')
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    @login_required
    def add_report(self):
        if request.method == 'POST':
            beach = request.form.get('beach')
            date = request.form.get('date')
            enterococcicount = request.form.get('enterococcicount')

            # Process the report data and save to the database
            new_report = {
                "_id": ObjectId(),
                "beach": beach,
                "date": date,
                "enterococcicount": enterococcicount,
            }
            self.reports_collection.insert_one(new_report)  # Assuming you are using MongoDB
            return redirect(url_for('admin_dashboard'))
        return render_template('add_report.html')
   
    @login_required
    def community_report(self):
     if request.method == 'POST':
        problem_type = request.form.get('problem_type')
        problem_description = request.form.get('problem_description')
        user_id = request.form.get('user_id')
        beach  = request.form.get('beach')

        # Validate the input fields
        if not problem_type or not problem_description or not beach:
            flash('Please fill out all fields.', 'danger')
            return redirect(url_for('community_report'))

        # Validate beach_id
        if not self.beaches_collection.find_one({'_id': ObjectId(beach)}):
            flash('Invalid beach ID.', 'danger')
            return redirect(url_for('community_report'))

        # Create a new CommunityReport instance
    
        new_community_report ={
            'problem_type': problem_type,
            'problem_description': problem_description,
            'user_id': user_id,
            'beach': beach,
            'date': datetime.now()
        }
        # Insert the report into the database
    
        self.community_reports_collection.insert_one(new_community_report)

        flash('Report submitted successfully!', 'success')
        return redirect(url_for('community_report'))

    # Retrieve the list of beaches and problem types
     beaches = list(self.beaches_collection.find())
     problem_types = [
        'Pollution',
        'Safety Issue',
        'Lack of Facilities',
        'Maintenance',
        'Other'
     ]
     return render_template('community_report.html', beaches=beaches, problem_types=problem_types)
       


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
    
    # Serve the image from GridFS
    def get_image(self, file_id):
        try:
            image_file = self.fs.get(ObjectId(file_id))  # Fetch the image using GridFS file ID
            return send_file(BytesIO(image_file.read()), mimetype='image/jpeg')  # Adjust MIME type as needed
        except Exception as e:
            flash(f"Image not found: {str(e)}", "danger")
            return redirect(url_for('home'))

    def run(self):
        self.app.run(debug=True)

if __name__ == '__main__':
    app = SeaClearApp()
    app.run()