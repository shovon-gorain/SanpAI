import os
import uuid
import random
from datetime import datetime
from PIL import Image, ImageFilter, ImageEnhance
import moviepy.editor as mp
from moviepy.video.fx.all import fadein, fadeout
import numpy as np
from scipy.io import wavfile
import librosa
import soundfile as sf

class VideoProcessor:
    def __init__(self, upload_folder):
        self.upload_folder = upload_folder
        self.effects = [
            'fade', 'zoom', 'pan', 'blur', 'contrast',
            'black_white', 'sepia', 'vignette'
        ]
        
    def organize_images(self, image_paths):
        """Organize images in a meaningful order"""
        # Sort by creation date if available, otherwise by filename
        try:
            # Try to get EXIF data for date taken
            image_paths.sort(key=lambda x: Image.open(x)._getexif().get(36867, 0) 
                           if Image.open(x)._getexif() else 0)
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
        # Organize images
        organized_images = self.organize_images(image_paths)
        
        if not organized_images:
            return False
            
        # Process music if provided
        audio_clip = None
        if music_path and os.path.exists(music_path):
            processed_audio = self.process_music(music_path, music_style)
            
            if processed_audio:
                y, sr = processed_audio
                # Save processed audio temporarily
                temp_audio_path = os.path.join(self.upload_folder, f"temp_audio_{uuid.uuid4().hex}.wav")
                sf.write(temp_audio_path, y, sr)
                
                # Load as moviepy audio clip
                try:
                    audio_clip = mp.AudioFileClip(temp_audio_path)
                except:
                    audio_clip = None
            else:
                # Fallback to original music
                try:
                    audio_clip = mp.AudioFileClip(music_path)
                except:
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
            return False
            
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
        if music_path and os.path.exists(music_path) and 'temp_audio_' in music_path:
            try:
                os.remove(music_path)
            except:
                pass
                
        return True