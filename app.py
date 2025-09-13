# from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory
# from database import (
#     init_db,
#     add_user,
#     get_user_by_email,
#     get_all_users,
#     get_all_videos,
#     increment_login_attempts,
#     reset_login_attempts,
#     get_login_attempts,
#     add_video,
#     get_videos_by_user,
#     update_payment_status
# )
# from werkzeug.security import generate_password_hash, check_password_hash
# import os
# from functools import wraps
# import psutil
# import datetime
# import uuid
# import random
# from PIL import Image, ImageFilter, ImageEnhance
# import moviepy.editor as mp
# from moviepy.video.fx.all import fadein, fadeout
# import numpy as np
# import librosa
# import soundfile as sf

# app = Flask(__name__)

# # Use environment SECRET_KEY in production. Fallback to placeholder for local dev.
# app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# # Initialize DB
# init_db()

# # Configure upload folder
# app.config['UPLOAD_FOLDER'] = 'uploads'
# app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# # Video Processor Class
# class VideoProcessor:
#     def __init__(self, upload_folder):
#         self.upload_folder = upload_folder
#         self.effects = [
#             'fade', 'zoom', 'pan', 'blur', 'contrast',
#             'black_white', 'sepia', 'vignette'
#         ]
        
#     def organize_images(self, image_paths):
#         """Organize images in a meaningful order"""
#         try:
#             # Try to get EXIF data for date taken
#             def get_date_taken(path):
#                 try:
#                     img = Image.open(path)
#                     exif = img._getexif()
#                     if exif and 36867 in exif:  # DateTimeOriginal
#                         return exif[36867]
#                 except:
#                     pass
#                 return "0"
            
#             image_paths.sort(key=lambda x: get_date_taken(x))
#         except:
#             # Fallback to filename sorting
#             image_paths.sort()
        
#         return image_paths
    
#     def apply_effect(self, image, effect_name):
#         """Apply visual effect to image"""
#         img = image.copy()
        
#         if effect_name == 'blur':
#             return img.filter(ImageFilter.GaussianBlur(2))
#         elif effect_name == 'contrast':
#             enhancer = ImageEnhance.Contrast(img)
#             return enhancer.enhance(1.5)
#         elif effect_name == 'black_white':
#             return img.convert('L')
#         elif effect_name == 'sepia':
#             # Create sepia tone
#             sepia = img.convert('RGB')
#             width, height = sepia.size
#             pixels = sepia.load()
            
#             for py in range(height):
#                 for px in range(width):
#                     r, g, b = sepia.getpixel((px, py))
                    
#                     tr = int(0.393 * r + 0.769 * g + 0.189 * b)
#                     tg = int(0.349 * r + 0.686 * g + 0.168 * b)
#                     tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                    
#                     pixels[px, py] = (min(tr, 255), min(tg, 255), min(tb, 255))
            
#             return sepia
#         elif effect_name == 'vignette':
#             # Apply vignette effect
#             img = img.convert('RGB')
#             width, height = img.size
#             pixels = img.load()
            
#             for y in range(height):
#                 for x in range(width):
#                     # Calculate distance from center
#                     dx = abs(x - width/2) / (width/2)
#                     dy = abs(y - height/2) / (height/2)
#                     d = (dx**2 + dy**2) ** 0.5
                    
#                     # Darken based on distance from center
#                     r, g, b = pixels[x, y]
#                     factor = 1 - d * 0.7  # 0.7 is vignette strength
#                     pixels[x, y] = (
#                         int(r * factor),
#                         int(g * factor),
#                         int(b * factor)
#                     )
            
#             return img
        
#         return img
    
#     def process_music(self, music_path, style):
#         """Process music according to selected style"""
#         if not os.path.exists(music_path):
#             return None
            
#         try:
#             # Load audio file
#             y, sr = librosa.load(music_path)
            
#             # Apply style-specific processing
#             if style == 'pop':
#                 # Increase tempo slightly, add compression
#                 y_fast = librosa.effects.time_stretch(y, rate=1.1)
#                 return y_fast, sr
                
#             elif style == 'rock':
#                 # Add distortion and increase bass
#                 y_distorted = np.tanh(y * 1.5)  # Simple distortion
#                 return y_distorted, sr
                
#             elif style == 'electronic':
#                 # Add synthetic elements and beat
#                 # Generate a simple synth beat
#                 beat_freq = 200
#                 t = np.linspace(0, len(y)/sr, len(y))
#                 beat = 0.3 * np.sin(2 * np.pi * beat_freq * t)
#                 y_electronic = y + beat
#                 return y_electronic, sr
                
#             elif style == 'hiphop':
#                 # Add heavier beats and lower pitch
#                 y_slow = librosa.effects.time_stretch(y, rate=0.9)
#                 # Add a simple beat
#                 beat = np.zeros_like(y_slow)
#                 beat[::sr//2] = 0.5  # Add beat every half second
#                 y_hiphop = y_slow + beat
#                 return y_hiphop, sr
                
#             elif style == 'chill':
#                 # Slow down and add reverb
#                 y_slow = librosa.effects.time_stretch(y, rate=0.85)
#                 # Simple reverb effect
#                 reverbed = np.convolve(y_slow, [0.6, 0.3, 0.1], mode='same')
#                 return reverbed, sr
                
#             else:
#                 # Return original for unknown styles
#                 return y, sr
                
#         except Exception as e:
#             print(f"Music processing error: {e}")
#             return None
    
#     def create_video(self, image_paths, music_path, music_style, output_path):
#         """Create video from images and music"""
#         try:
#             # Organize images
#             organized_images = self.organize_images(image_paths)
            
#             if not organized_images:
#                 return False, "No valid images found"
                
#             # Process music if provided
#             audio_clip = None
#             temp_audio_path = None
#             if music_path and os.path.exists(music_path):
#                 try:
#                     processed_audio = self.process_music(music_path, music_style)
                    
#                     if processed_audio:
#                         y, sr = processed_audio
#                         # Save processed audio temporarily
#                         temp_audio_path = os.path.join(self.upload_folder, f"temp_audio_{uuid.uuid4().hex}.wav")
#                         sf.write(temp_audio_path, y, sr)
                        
#                         # Load as moviepy audio clip
#                         try:
#                             audio_clip = mp.AudioFileClip(temp_audio_path)
#                         except Exception as e:
#                             print(f"Error loading audio: {e}")
#                             audio_clip = None
#                     else:
#                         # Fallback to original music
#                         try:
#                             audio_clip = mp.AudioFileClip(music_path)
#                         except Exception as e:
#                             print(f"Error loading original audio: {e}")
#                             audio_clip = None
#                 except Exception as e:
#                     print(f"Error processing music: {e}")
#                     audio_clip = None
            
#             # Create video clips from images
#             clips = []
#             duration_per_image = 3  # seconds per image
            
#             for img_path in organized_images:
#                 try:
#                     # Apply random effect to each image
#                     img = Image.open(img_path)
#                     effect = random.choice(self.effects)
#                     processed_img = self.apply_effect(img, effect)
                    
#                     # Save processed image temporarily
#                     temp_img_path = os.path.join(self.upload_folder, f"temp_{uuid.uuid4().hex}.jpg")
#                     processed_img.save(temp_img_path)
                    
#                     # Create clip with fade in/out
#                     clip = mp.ImageClip(temp_img_path).set_duration(duration_per_image)
#                     clip = clip.fx(fadein, 0.5).fx(fadeout, 0.5)
#                     clips.append(clip)
                    
#                     # Clean up temporary image
#                     os.remove(temp_img_path)
                    
#                 except Exception as e:
#                     print(f"Error processing image {img_path}: {e}")
#                     continue
            
#             if not clips:
#                 return False, "No valid video clips created"
                
#             # Concatenate all clips
#             video = mp.concatenate_videoclips(clips, method="compose")
            
#             # Add audio if available
#             if audio_clip:
#                 # Trim or loop audio to match video duration
#                 if audio_clip.duration < video.duration:
#                     # Loop audio
#                     audio_clip = audio_clip.loop(duration=video.duration)
#                 else:
#                     # Trim audio to video duration
#                     audio_clip = audio_clip.subclip(0, video.duration)
                    
#                 video = video.set_audio(audio_clip)
            
#             # Write video file
#             video.write_videofile(
#                 output_path,
#                 fps=24,
#                 codec='libx264',
#                 audio_codec='aac',
#                 verbose=False,
#                 logger=None
#             )
            
#             # Clean up temporary audio file
#             if temp_audio_path and os.path.exists(temp_audio_path):
#                 try:
#                     os.remove(temp_audio_path)
#                 except:
#                     pass
                    
#             return True, "Video created successfully"
            
#         except Exception as e:
#             print(f"Error in create_video: {e}")
#             return False, f"Video creation failed: {str(e)}"

# # Initialize video processor
# video_processor = VideoProcessor(app.config['UPLOAD_FOLDER'])

# # ------------------------------
# # Decorators
# # ------------------------------
# def login_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if 'user_id' not in session:
#             flash('Please login to continue.')
#             return redirect(url_for('auth'))
#         return f(*args, **kwargs)
#     return decorated_function


# def admin_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if not session.get('is_admin', False):
#             flash('Admin access required.')
#             return redirect(url_for('index'))
#         return f(*args, **kwargs)
#     return decorated_function


# def payment_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if not session.get('is_paid', False) and not session.get('is_admin', False):
#             flash('Payment required to access this feature.')
#             return redirect(url_for('payment'))
#         return f(*args, **kwargs)
#     return decorated_function


# # ------------------------------
# # Routes
# # ------------------------------
# @app.route('/')
# def index():
#     return render_template('index.html', user=session.get('user'))


# @app.route('/auth', methods=['GET', 'POST'])
# def auth():
#     if request.method == 'POST':
#         action = request.form.get('action')
#         email = request.form.get('email', '').strip().lower()
#         password = request.form.get('password', '')
#         user_type = request.form.get('user_type', 'user')

#         attempts = get_login_attempts(email) if email else 0
#         if attempts >= 3 and action == 'login':
#             flash('Account temporarily locked due to too many failed attempts. Try again later.')
#             return render_template('auth.html')

#         if action == 'login':
#             user = get_user_by_email(email)
#             if user and check_password_hash(user[3], password):
#                 # Check if user type matches
#                 if (user_type == 'admin' and user[4] != 1) or (user_type == 'user' and user[4] == 1):
#                     flash('Invalid login type for this account.')
#                     return render_template('auth.html')
                
#                 session['user_id'] = user[0]
#                 session['user'] = {
#                     'id': user[0],
#                     'name': user[1],
#                     'email': user[2],
#                     'is_admin': True if user[4] == 1 else False,
#                     'is_paid': True if user[5] == 1 else False
#                 }
#                 session['is_admin'] = True if user[4] == 1 else False
#                 session['is_paid'] = True if user[5] == 1 else False

#                 reset_login_attempts(email)
#                 flash('Login successful!')

#                 if session['is_admin']:
#                     return redirect(url_for('admin_dashboard'))
#                 elif session['is_paid']:
#                     return redirect(url_for('dashboard'))
#                 else:
#                     return redirect(url_for('payment'))
#             else:
#                 increment_login_attempts(email)
#                 flash('Invalid email or password.')
#                 return render_template('auth.html')

#         elif action == 'register':
#             if user_type == 'admin':
#                 flash('Admin accounts cannot be registered.')
#                 return render_template('auth.html')
                
#             name = request.form.get('name', '').strip()
#             confirm_password = request.form.get('confirm_password', '')

#             if not name or not email or not password:
#                 flash('Please fill all required fields.')
#                 return render_template('auth.html')
#             if password != confirm_password:
#                 flash('Passwords do not match.')
#                 return render_template('auth.html')
#             if get_user_by_email(email):
#                 flash('Email already registered. Please login.')
#                 return render_template('auth.html')

#             hashed = generate_password_hash(password)
#             add_user(name, email, hashed, 0, 0)  # Regular user, not paid initially
#             flash('Registration successful! Please login.')
#             return redirect(url_for('auth'))

#         else:
#             flash('Unknown action.')
#             return render_template('auth.html')

#     return render_template('auth.html')


# @app.route('/payment', methods=['GET', 'POST'])
# @login_required
# def payment():
#     if request.method == 'POST':
#         # Simulate payment processing
#         plan = request.form.get('plan')
        
#         # Update user payment status in database
#         update_payment_status(session['user_id'], 1)
#         session['is_paid'] = True
#         session['user']['is_paid'] = True
        
#         flash('Payment successful! You can now access the dashboard.')
#         return redirect(url_for('dashboard'))
    
#     return render_template('payment.html')


# @app.route('/payment/success')
# @login_required
# def payment_success():
#     return render_template('success.html')


# @app.route('/admin')
# @login_required
# @admin_required
# def admin_dashboard():
#     users = get_all_users()
#     videos = get_all_videos()
#     total_users = len(users) if users else 0
#     total_reels = len(videos) if videos else 0
#     return render_template('admin.html', users=users, videos=videos,
#                            total_users=total_users, total_reels=total_reels)


# @app.route('/dashboard')
# @login_required
# @payment_required
# def dashboard():
#     # Get user's videos from database
#     user_videos = get_videos_by_user(session['user_id'])
#     return render_template('dashboard.html', user=session.get('user'), videos=user_videos)


# @app.route('/logout')
# def logout():
#     session.clear()
#     flash('You have been logged out.')
#     return redirect(url_for('index'))


# @app.route('/create', methods=['GET'])
# @login_required
# @payment_required
# def create():
#     return render_template('index.html', user=session.get('user'))


# @app.route('/generate_video', methods=['POST'])
# @login_required
# @payment_required
# def generate_video():
#     photos = request.files.getlist('photos')
#     music_style = request.form.get('music_style', 'electronic')
#     custom_music = request.files.get('custom_music')
    
#     # Validate number of photos
#     if len(photos) < 5 or len(photos) > 10:
#         return jsonify({
#             'success': False,
#             'message': 'Please select between 5 and 10 photos.'
#         })

#     # Create upload directory if it doesn't exist
#     upload_dir = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
#     if not os.path.exists(upload_dir):
#         os.makedirs(upload_dir, exist_ok=True)

#     # Save uploaded photos
#     saved_files = []
#     for photo in photos:
#         if photo and photo.filename:
#             # Generate a unique filename
#             file_ext = os.path.splitext(photo.filename)[1]
#             unique_filename = f"{uuid.uuid4().hex}{file_ext}"
#             save_path = os.path.join(upload_dir, unique_filename)
#             photo.save(save_path)
#             saved_files.append(save_path)

#     # Save custom music if provided
#     music_filename = None
#     if custom_music and custom_music.filename:
#         file_ext = os.path.splitext(custom_music.filename)[1]
#         music_filename = f"music_{uuid.uuid4().hex}{file_ext}"
#         save_path = os.path.join(upload_dir, music_filename)
#         custom_music.save(save_path)

#     # Generate a unique video filename
#     video_filename = f"{uuid.uuid4().hex}.mp4"
#     video_path = os.path.join(upload_dir, video_filename)
    
#     # Create video using our processor
#     success, message = video_processor.create_video(
#         saved_files,
#         os.path.join(upload_dir, music_filename) if music_filename else None,
#         music_style,
#         video_path
#     )
    
#     if not success:
#         # Clean up uploaded files
#         for file_path in saved_files:
#             try:
#                 os.remove(file_path)
#             except:
#                 pass
#         if music_filename:
#             try:
#                 os.remove(os.path.join(upload_dir, music_filename))
#             except:
#                 pass
#         return jsonify({
#             'success': False,
#             'message': message
#         })
    
#     # Add video to database
#     add_video(
#         user_id=session['user_id'],
#         video_url=video_filename,
#         music_style=music_style,
#         title=f"Video_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
#         music_file=music_filename
#     )

#     # Clean up uploaded photos
#     for file_path in saved_files:
#         try:
#             os.remove(file_path)
#         except:
#             pass

#     return jsonify({
#         'success': True,
#         'message': message,
#         'video_url': video_filename
#     })


# @app.route('/uploads/<filename>')
# @login_required
# def download_file(filename):
#     return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# @app.route('/api/user/videos')
# @login_required
# def api_user_videos():
#     # Get user's videos from database
#     user_videos = get_videos_by_user(session['user_id'])
    
#     # Format videos for JSON response
#     videos_data = []
#     for video in user_videos:
#         videos_data.append({
#             'id': video['id'],
#             'title': video['title'],
#             'video_url': url_for('download_file', filename=video['video_url']),
#             'music_style': video['music_style'],
#             'created_at': video['created_at']
#         })
    
#     return jsonify(videos_data)


# # ------------------------------
# # API Endpoints for Admin Dashboard
# # ------------------------------
# @app.route('/api/online-users')
# def api_online_users():
#     users = get_all_users()
#     return jsonify({"online_users": len(users)})


# @app.route('/api/system-metrics')
# def api_system_metrics():
#     cpu = psutil.cpu_percent(interval=0.5)
#     mem = psutil.virtual_memory().percent
#     disk = psutil.disk_usage('/').percent
#     net = psutil.net_io_counters()
#     return jsonify({
#         "cpu": cpu,
#         "memory": mem,
#         "disk": disk,
#         "net_in": net.bytes_recv,
#         "net_out": net.bytes_sent,
#         "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
#     })


# @app.route('/api/logs')
# def api_logs():
#     logs = [
#         {"message": "System started", "time": "09:00:00"},
#         {"message": "Admin logged in", "time": "09:05:22"},
#         {"message": "Video generated", "time": "09:10:11"}
#     ]
#     return jsonify({"logs": logs})


# # ------------------------------
# # App startup
# # ------------------------------
# if __name__ == '__main__':
#     uploads_folder = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
#     if not os.path.exists(uploads_folder):
#         os.makedirs(uploads_folder, exist_ok=True)
#     app.run(debug=True)


from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory
from database import (
    init_db,
    add_user,
    get_user_by_email,
    get_all_users,
    get_all_videos,
    increment_login_attempts,
    reset_login_attempts,
    get_login_attempts,
    add_video,
    get_videos_by_user,
    update_payment_status
)
from werkzeug.security import generate_password_hash, check_password_hash
import os
from functools import wraps
import psutil
import datetime
import uuid
import random
from PIL import Image, ImageFilter, ImageEnhance
import moviepy.editor as mp
from moviepy.video.fx.all import fadein, fadeout
import numpy as np
import librosa
import soundfile as sf

app = Flask(__name__)

# Use environment SECRET_KEY in production. Fallback to placeholder for local dev.
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Initialize DB
init_db()

# Configure upload folder
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Video Processor Class
class VideoProcessor:
    def __init__(self, upload_folder):
        self.upload_folder = upload_folder
        self.effects = [
            'fade', 'zoom', 'pan', 'blur', 'contrast',
            'black_white', 'sepia', 'vignette'
        ]
        
    def organize_images(self, image_paths):
        """Organize images in a meaningful order"""
        try:
            # Try to get EXIF data for date taken
            def get_date_taken(path):
                try:
                    img = Image.open(path)
                    exif = img._getexif()
                    if exif and 36867 in exif:  # DateTimeOriginal
                        return exif[36867]
                except:
                    pass
                return "0"
            
            image_paths.sort(key=lambda x: get_date_taken(x))
        except:
            # Fallback to filename sorting
            image_paths.sort()
        
        return image_paths
    
    def apply_effect(self, image, effect_name):
        """Apply visual effect to image"""
        img = image.copy()
        
        if effect_name == 'blur':
            return img.filter(ImageFilter.GaussianBlur(2))
        elif effect_name == 'contrast':
            enhancer = ImageEnhance.Contrast(img)
            return enhancer.enhance(1.5)
        elif effect_name == 'black_white':
            return img.convert('L')
        elif effect_name == 'sepia':
            # Create sepia tone
            sepia = img.convert('RGB')
            width, height = sepia.size
            pixels = sepia.load()
            
            for py in range(height):
                for px in range(width):
                    r, g, b = sepia.getpixel((px, py))
                    
                    tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                    tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                    tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                    
                    pixels[px, py] = (min(tr, 255), min(tg, 255), min(tb, 255))
            
            return sepia
        elif effect_name == 'vignette':
            # Apply vignette effect
            img = img.convert('RGB')
            width, height = img.size
            pixels = img.load()
            
            for y in range(height):
                for x in range(width):
                    # Calculate distance from center
                    dx = abs(x - width/2) / (width/2)
                    dy = abs(y - height/2) / (height/2)
                    d = (dx**2 + dy**2) ** 0.5
                    
                    # Darken based on distance from center
                    r, g, b = pixels[x, y]
                    factor = 1 - d * 0.7  # 0.7 is vignette strength
                    pixels[x, y] = (
                        int(r * factor),
                        int(g * factor),
                        int(b * factor)
                    )
            
            return img
        
        return img
    
    def process_music(self, music_path, style):
        """Process music according to selected style"""
        if not os.path.exists(music_path):
            return None
            
        try:
            # Load audio file
            y, sr = librosa.load(music_path)
            
            # Apply style-specific processing
            if style == 'pop':
                # Increase tempo slightly, add compression
                y_fast = librosa.effects.time_stretch(y, rate=1.1)
                return y_fast, sr
                
            elif style == 'rock':
                # Add distortion and increase bass
                y_distorted = np.tanh(y * 1.5)  # Simple distortion
                return y_distorted, sr
                
            elif style == 'electronic':
                # Add synthetic elements and beat
                # Generate a simple synth beat
                beat_freq = 200
                t = np.linspace(0, len(y)/sr, len(y))
                beat = 0.3 * np.sin(2 * np.pi * beat_freq * t)
                y_electronic = y + beat
                return y_electronic, sr
                
            elif style == 'hiphop':
                # Add heavier beats and lower pitch
                y_slow = librosa.effects.time_stretch(y, rate=0.9)
                # Add a simple beat
                beat = np.zeros_like(y_slow)
                beat[::sr//2] = 0.5  # Add beat every half second
                y_hiphop = y_slow + beat
                return y_hiphop, sr
                
            elif style == 'chill':
                # Slow down and add reverb
                y_slow = librosa.effects.time_stretch(y, rate=0.85)
                # Simple reverb effect
                reverbed = np.convolve(y_slow, [0.6, 0.3, 0.1], mode='same')
                return reverbed, sr
                
            else:
                # Return original for unknown styles
                return y, sr
                
        except Exception as e:
            print(f"Music processing error: {e}")
            return None
    
    def create_video(self, image_paths, music_path, music_style, output_path):
        """Create video from images and music"""
        try:
            # Organize images
            organized_images = self.organize_images(image_paths)
            
            if not organized_images:
                return False, "No valid images found"
                
            # Process music if provided
            audio_clip = None
            temp_audio_path = None
            if music_path and os.path.exists(music_path):
                try:
                    processed_audio = self.process_music(music_path, music_style)
                    
                    if processed_audio:
                        y, sr = processed_audio
                        # Save processed audio temporarily
                        temp_audio_path = os.path.join(self.upload_folder, f"temp_audio_{uuid.uuid4().hex}.wav")
                        sf.write(temp_audio_path, y, sr)
                        
                        # Load as moviepy audio clip
                        try:
                            audio_clip = mp.AudioFileClip(temp_audio_path)
                        except Exception as e:
                            print(f"Error loading audio: {e}")
                            audio_clip = None
                    else:
                        # Fallback to original music
                        try:
                            audio_clip = mp.AudioFileClip(music_path)
                        except Exception as e:
                            print(f"Error loading original audio: {e}")
                            audio_clip = None
                except Exception as e:
                    print(f"Error processing music: {e}")
                    audio_clip = None
            
            # Create video clips from images
            clips = []
            duration_per_image = 3  # seconds per image
            
            for img_path in organized_images:
                try:
                    # Apply random effect to each image
                    img = Image.open(img_path)
                    effect = random.choice(self.effects)
                    processed_img = self.apply_effect(img, effect)
                    
                    # Save processed image temporarily
                    temp_img_path = os.path.join(self.upload_folder, f"temp_{uuid.uuid4().hex}.jpg")
                    processed_img.save(temp_img_path)
                    
                    # Create clip with fade in/out
                    clip = mp.ImageClip(temp_img_path).set_duration(duration_per_image)
                    clip = clip.fx(fadein, 0.5).fx(fadeout, 0.5)
                    clips.append(clip)
                    
                    # Clean up temporary image
                    os.remove(temp_img_path)
                    
                except Exception as e:
                    print(f"Error processing image {img_path}: {e}")
                    continue
            
            if not clips:
                return False, "No valid video clips created"
                
            # Concatenate all clips
            video = mp.concatenate_videoclips(clips, method="compose")
            
            # Add audio if available
            if audio_clip:
                # Trim or loop audio to match video duration
                if audio_clip.duration < video.duration:
                    # Loop audio
                    audio_clip = audio_clip.loop(duration=video.duration)
                else:
                    # Trim audio to video duration
                    audio_clip = audio_clip.subclip(0, video.duration)
                    
                video = video.set_audio(audio_clip)
            
            # Write video file
            video.write_videofile(
                output_path,
                fps=24,
                codec='libx264',
                audio_codec='aac',
                verbose=False,
                logger=None
            )
            
            # Clean up temporary audio file
            if temp_audio_path and os.path.exists(temp_audio_path):
                try:
                    os.remove(temp_audio_path)
                except:
                    pass
                    
            return True, "Video created successfully"
            
        except Exception as e:
            print(f"Error in create_video: {e}")
            return False, f"Video creation failed: {str(e)}"

# Initialize video processor
video_processor = VideoProcessor(app.config['UPLOAD_FOLDER'])

# ------------------------------
# Decorators
# ------------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to continue.')
            return redirect(url_for('auth'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin', False):
            flash('Admin access required.')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def payment_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_paid', False) and not session.get('is_admin', False):
            flash('Payment required to access this feature.')
            return redirect(url_for('payment'))
        return f(*args, **kwargs)
    return decorated_function


# ------------------------------
# Routes
# ------------------------------
@app.route('/')
def index():
    return render_template('index.html', user=session.get('user'))


@app.route('/auth', methods=['GET', 'POST'])
def auth():
    if request.method == 'POST':
        action = request.form.get('action')
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user_type = request.form.get('user_type', 'user')

        attempts = get_login_attempts(email) if email else 0
        if attempts >= 3 and action == 'login':
            flash('Account temporarily locked due to too many failed attempts. Try again later.')
            return render_template('auth.html')

        if action == 'login':
            user = get_user_by_email(email)
            if user and check_password_hash(user[3], password):
                # Check if user type matches
                if (user_type == 'admin' and user[4] != 1) or (user_type == 'user' and user[4] == 1):
                    flash('Invalid login type for this account.')
                    return render_template('auth.html')
                
                session['user_id'] = user[0]
                session['user'] = {
                    'id': user[0],
                    'name': user[1],
                    'email': user[2],
                    'is_admin': True if user[4] == 1 else False,
                    'is_paid': True if user[5] == 1 else False
                }
                session['is_admin'] = True if user[4] == 1 else False
                session['is_paid'] = True if user[5] == 1 else False

                reset_login_attempts(email)
                flash('Login successful!')

                if session['is_admin']:
                    return redirect(url_for('admin_dashboard'))
                elif session['is_paid']:
                    return redirect(url_for('dashboard'))
                else:
                    return redirect(url_for('payment'))
            else:
                increment_login_attempts(email)
                flash('Invalid email or password.')
                return render_template('auth.html')

        elif action == 'register':
            if user_type == 'admin':
                flash('Admin accounts cannot be registered.')
                return render_template('auth.html')
                
            name = request.form.get('name', '').strip()
            confirm_password = request.form.get('confirm_password', '')

            if not name or not email or not password:
                flash('Please fill all required fields.')
                return render_template('auth.html')
            if password != confirm_password:
                flash('Passwords do not match.')
                return render_template('auth.html')
            if get_user_by_email(email):
                flash('Email already registered. Please login.')
                return render_template('auth.html')

            hashed = generate_password_hash(password)
            add_user(name, email, hashed, 0, 0)  # Regular user, not paid initially
            flash('Registration successful! Please login.')
            return redirect(url_for('auth'))

        else:
            flash('Unknown action.')
            return render_template('auth.html')

    return render_template('auth.html')


@app.route('/payment', methods=['GET', 'POST'])
@login_required
def payment():
    if request.method == 'POST':
        # Simulate payment processing
        plan = request.form.get('plan')
        
        # Update user payment status in database
        update_payment_status(session['user_id'], 1)
        session['is_paid'] = True
        session['user']['is_paid'] = True
        
        flash('Payment successful! You can now access the dashboard.')
        return redirect(url_for('dashboard'))
    
    return render_template('payment.html')


@app.route('/payment/success')
@login_required
def payment_success():
    return render_template('success.html')


@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    try:
        users = get_all_users()
        videos = get_all_videos()
        total_users = len(users) if users else 0
        total_reels = len(videos) if videos else 0
        return render_template('admin.html', users=users, videos=videos,
                               total_users=total_users, total_reels=total_reels)
    except Exception as e:
        flash('Error accessing admin panel: ' + str(e))
        return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
@payment_required
def dashboard():
    # Get user's videos from database
    user_videos = get_videos_by_user(session['user_id'])
    return render_template('dashboard.html', user=session.get('user'), videos=user_videos)


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('index'))


@app.route('/create', methods=['GET'])
@login_required
@payment_required
def create():
    return render_template('index.html', user=session.get('user'))


@app.route('/generate_video', methods=['POST'])
@login_required
@payment_required
def generate_video():
    photos = request.files.getlist('photos')
    music_style = request.form.get('music_style', 'electronic')
    custom_music = request.files.get('custom_music')
    
    # Validate number of photos
    if len(photos) < 5 or len(photos) > 10:
        return jsonify({
            'success': False,
            'message': 'Please select between 5 and 10 photos.'
        })

    # Create upload directory if it doesn't exist
    upload_dir = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir, exist_ok=True)

    # Save uploaded photos
    saved_files = []
    for photo in photos:
        if photo and photo.filename:
            # Generate a unique filename
            file_ext = os.path.splitext(photo.filename)[1]
            unique_filename = f"{uuid.uuid4().hex}{file_ext}"
            save_path = os.path.join(upload_dir, unique_filename)
            photo.save(save_path)
            saved_files.append(save_path)

    # Save custom music if provided
    music_filename = None
    if custom_music and custom_music.filename:
        file_ext = os.path.splitext(custom_music.filename)[1]
        music_filename = f"music_{uuid.uuid4().hex}{file_ext}"
        save_path = os.path.join(upload_dir, music_filename)
        custom_music.save(save_path)

    # Generate a unique video filename
    video_filename = f"{uuid.uuid4().hex}.mp4"
    video_path = os.path.join(upload_dir, video_filename)
    
    # Create video using our processor
    success, message = video_processor.create_video(
        saved_files,
        os.path.join(upload_dir, music_filename) if music_filename else None,
        music_style,
        video_path
    )
    
    if not success:
        # Clean up uploaded files
        for file_path in saved_files:
            try:
                os.remove(file_path)
            except:
                pass
        if music_filename:
            try:
                os.remove(os.path.join(upload_dir, music_filename))
            except:
                pass
        return jsonify({
            'success': False,
            'message': message
        })
    
    # Add video to database
    add_video(
        user_id=session['user_id'],
        video_url=video_filename,
        music_style=music_style,
        title=f"Video_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
        music_file=music_filename
    )

    # Clean up uploaded photos
    for file_path in saved_files:
        try:
            os.remove(file_path)
        except:
            pass

    return jsonify({
        'success': True,
        'message': message,
        'video_url': video_filename
    })


@app.route('/uploads/<filename>')
@login_required
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/api/user/videos')
@login_required
def api_user_videos():
    # Get user's videos from database
    user_videos = get_videos_by_user(session['user_id'])
    
    # Format videos for JSON response
    videos_data = []
    for video in user_videos:
        videos_data.append({
            'id': video['id'],
            'title': video['title'],
            'video_url': url_for('download_file', filename=video['video_url']),
            'music_style': video['music_style'],
            'created_at': video['created_at']
        })
    
    return jsonify(videos_data)


# ------------------------------
# API Endpoints for Admin Dashboard
# ------------------------------
@app.route('/api/online-users')
def api_online_users():
    users = get_all_users()
    return jsonify({"online_users": len(users)})


@app.route('/api/system-metrics')
def api_system_metrics():
    cpu = psutil.cpu_percent(interval=0.5)
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    net = psutil.net_io_counters()
    return jsonify({
        "cpu": cpu,
        "memory": mem,
        "disk": disk,
        "net_in": net.bytes_recv,
        "net_out": net.bytes_sent,
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
    })


@app.route('/api/logs')
def api_logs():
    logs = [
        {"message": "System started", "time": "09:00:00"},
        {"message": "Admin logged in", "time": "09:05:22"},
        {"message": "Video generated", "time": "09:10:11"}
    ]
    return jsonify({"logs": logs})


# NEW ROUTES ADDED HERE
@app.route('/signup')
def signup():
    return redirect(url_for('auth'))


@app.route('/get-started')
def get_started():
    if 'user_id' in session:
        if session.get('is_paid', False):
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('payment'))
    else:
        return redirect(url_for('auth'))


# ERROR HANDLERS
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500


@app.errorhandler(403)
def forbidden_error(error):
    flash('Access forbidden. You do not have permission to access this page.')
    return redirect(url_for('index'))


# ------------------------------
# App startup
# ------------------------------
if __name__ == '__main__':
    uploads_folder = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
    if not os.path.exists(uploads_folder):
        os.makedirs(uploads_folder, exist_ok=True)
    app.run(debug=True)