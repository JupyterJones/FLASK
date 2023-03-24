#!/home/jack/Desktop/FLASK/flask_venv/bin/python
import subprocess
import logging
from flask import Flask, render_template, send_file, request, redirect, url_for, flash
from flask import jsonify, send_from_directory
import os
from logging.handlers import RotatingFileHandler
import datetime
from werkzeug.utils import secure_filename
import time
from clean_images import clean_images
from flask import Response
import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image
import pygame
import random
from datetime import datetime
from PIL import Image
from gtts import gTTS
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip
from io import BytesIO
import base64
import imageio
# Define the Flask application
app = Flask(__name__)

@app.route('/')
def index():
    image_dir = 'static/images'
    image_files = [f for f in os.listdir(image_dir) if f.endswith('.jpg')]
    random_image_file = random.choice(image_files)
    return render_template('index.html', random_image_file=random_image_file)


app.secret_key = os.urandom(24)

app.config['UPLOAD_FOLDER'] = 'static/images/uploads'
app.config['RESULTS_FOLDER'] = 'static/videos/results'
app.config['THUMBNAILS_FOLDER'] = 'static/images/thumbnails'
#app.config['CHECKPOINT_PATH'] = '/home/jack/Desktop/FlaskApp/Wav2Lip/checkpoints/wav2lip_gan.pth'
#app.config['AUDIO_PATH'] = '/home/jack/Desktop/FlaskApp/Wav2Lip/content/sample_data/input_audio.wav'

# Set the maximum file size to 16MB
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Configure the logger
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)
handler.setFormatter(formatter)
app.logger.addHandler(handler)

# Define route to display upload form
@app.route('/upload_file', methods=['POST', 'GET'])
def upload_file():
    if request.method == 'POST':
        # Check if file was uploaded
        if 'file' not in request.files:
            app.logger.error('No file was uploaded')
            flash('Error: No file was uploaded')
            return redirect(request.url)
        app.logger.error('request.files[\'file\']')
        file = request.files['file']

        # Check if file was selected
        if file.filename == '':
            app.logger.error('No file was selected')
            flash('Error: No file was selected')
            return redirect(request.url)

        # Define allowed file extensions
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

        # Define function to check file extension
        def allowed_file(filename):
            return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

        # Check if file is allowed
        if not allowed_file(file.filename):
            app.logger.error(f'File {file.filename} is not allowed')
            flash(f'Error: File {file.filename} is not allowed')
            return redirect(request.url)

        # Save the file
        try:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            app.logger.info(f'File {filename} saved')
        except Exception as e:
            app.logger.error(f'Error saving file: {e}')
            flash('Error: Unable to save file')
            return redirect(request.url)

        # Redirect to the result page
        return redirect(url_for('result', filename=filename))

    # Return the upload form for GET requests
    return render_template('upload_file.html')

@app.route('/result/<filename>')
def result(filename):
    return render_template('result.html', filename=filename)


@app.route('/process_images', methods=['POST', 'GET'])
def process_images():
    if request.method == 'POST':
        # read the images from the request
        img1 = Image.open(request.files['image1'].stream).convert('RGB')
        img2 = Image.open(request.files['image2'].stream).convert('L')
        img3 = Image.open(request.files['image3'].stream).convert('RGB')
    
        # resize the images to have the same shape
        img1 = img1.resize((img2.width, img2.height))
        img3 = img3.resize((img2.width, img2.height))
    
        # convert the mask to binary
        threshold = 127
        mask = Image.eval(img2, lambda px: 255 if px > threshold else 0)
    
        # apply the mask
        img = Image.composite(img1, img3, mask)
    
        # save the image to a file
        output = BytesIO()
        current_datetime = datetime.now()
        str_current_datetime = str(current_datetime)
        file_name = "static/images/"+str_current_datetime+"XXXX.jpg"
        img.save(file_name, format='JPEG')
        img.save(output, format='JPEG')
        output.seek(0)
    
        # encode the image to bytes
        img_bytes = output.getvalue()
    
        # return the image as a response
        return Response(img_bytes, mimetype='image/jpeg')
    return render_template('process_images.html')


@app.route('/blend_pil', methods=['POST', 'GET'])
def blend_pil():
    if request.method == 'POST':
        # Get the uploaded images
        img1 = request.files['img1']
        img2 = request.files['img2']
        img3 = request.files['img3']

        # Open the images using PIL
        img1_pil = Image.open(img1)
        img2_pil = Image.open(img2)
        img3_pil = Image.open(img3)

        # Blend the images
        blended_pil = Image.blend(img1_pil, img2_pil, 1/3)
        blended_pil = Image.blend(blended_pil, img3_pil, 1/3)

        # Return the blended image as a response
        # Since we are not saving it to the server, we can use a BytesIO object to avoid creating a temporary file
        img_io = BytesIO()
        blended_pil.save(img_io, 'JPEG', quality=70)
        current_datetime = datetime.now()
        str_current_datetime = str(current_datetime)
        file_name = "static/images/uploads/blended_pil"+str_current_datetime+"XXXX.jpg"
        blended_pil.save(file_name, format='JPEG')
        img_io.seek(0)
        
        # Generate the HTML for displaying the blended image in the template
        blended_image_data = base64.b64encode(img_io.getvalue()).decode('utf-8')
        blended_image_url = f"data:image/jpeg;base64,{blended_image_data}"
        #blended_image_url = blended_image_url.resize(( blended_image_url.size[0]//2, blended_image_url.size[1]//2), Image.ANTIALIAS) 
        # Pass the URL of the blended image to the template
        return render_template('show_blend_pil.html', blended_image_url=blended_image_url)      
    return render_template('blend_pil.html')
@app.route('/view_thumbs')
def view_thumbs():
    # Define the directory where the images are located
    image_directory = '/home/jack/Desktop/FLASK/static/images/uploads'
    # Get a list of all the image files in the directory
    image_files = [f for f in os.listdir(image_directory) if f.endswith('.jpg') or f.endswith('.png')]
    # Create a list of dictionaries containing the image file name and URL
    image_list = [{'name': f, 'url': f'/images/uploads/{f}'} for f in image_files]
    # Render the template with the list of images
    return render_template('view_thumbs.html', image_list=image_list)



@app.route('/images/uploads/<filename>')
def image(filename):
    # Define the directory where the images are located
    image_directory = '/home/jack/Desktop/FLASK/static/images/uploads'
    # Generate the full path to the requested image file
    image_path = os.path.join(image_directory, filename)
    # Determine the file type based on the file extension
    file_extension = os.path.splitext(filename)[1].lower()
    if file_extension == '.jpg':
        content_type = 'image/jpeg'
    elif file_extension == '.png':
        content_type = 'image/png'
    else:
        # If the file type is not recognized, return a 404 error
        print("abort(404)")
    # Return the image file as a response with the appropriate content type
    with open(image_path, 'rb') as f:
        image_data = f.read()
    return Response(image_data, content_type=content_type)

@app.route('/add_border')
def add_border():
    images = [f for f in os.listdir('static/images/uploads/') if os.path.isfile(os.path.join('static/images/uploads/', f))]
    thumbnails = []
    for image in images:
        with Image.open('static/images/uploads/'+image) as img:
            img.thumbnail((200, 200))
            thumbnail_name = 'thumbnail_'+image
            img.save('static/thumbnails/'+thumbnail_name)
            thumbnails.append(thumbnail_name)
    return render_template('add_border.html', images=images, thumbnails=thumbnails)


@app.route('/select_border')
def select_border():
    borders = os.listdir('static/transparent_borders/')
    return render_template('select_border.html', borders=borders)

@app.route('/apply_border', methods=['POST', 'GET'])
def apply_border():
    selected_image = request.form['image']
    selected_border = request.form['border']
    try:
        with Image.open('static/images/uploads/'+selected_image) as img:
            with Image.open('static/transparent_borders/'+selected_border) as border:
                img = img.resize(border.size)
                img.paste(border, (0, 0), border)
                final_image_name = 'final_'+selected_image
                img.save('static/final_images/'+final_image_name)
        return render_template('final_image.html', final_image=final_image_name, message='Border applied successfully.')
    except Exception as e:
        error_message = f'An error occurred: {str(e)}. Please try again.'
        return render_template('apply_border.html', image=selected_image, border=selected_border, error_message=error_message)

@app.route('/select_border_image', methods=['GET'])
def select_border_image():
    try:
        image = request.args.get('image')
        if not image:
            raise ValueError('No image selected.')
        return render_template('select_border.html', image=image, borders=os.listdir('static/transparent_borders/'))
    except Exception as e:
        error_message = f'An error occurred: {str(e)}. Please try again.'
        return render_template('add_border.html', error_message=error_message)

@app.route("/make_animation")
def make_animation():
    # Get a list of all files in the final_images directory
    image_files = os.listdir("static/final_images/")

    # Select 20 random files from the list
    selected_files = random.sample(image_files, 20)
    
    # Load each selected file, resize it to 400x600, and save it to a temporary directory
    resized_images = []
    for filename in selected_files:
        with Image.open("static/final_images/" + filename) as img:
            img = img.resize((400, 600))
            temp_filename = "static/tmp/" + filename
            img.save(temp_filename)
            resized_images.append(temp_filename)
    
    # Create an animated GIF from the resized images
 
    gif_filename = "static/animated_gifs/animated.gif"
    with imageio.get_writer(gif_filename, mode='I', duration=1) as writer:
        for filename in resized_images:
            image = imageio.imread(filename)
            writer.append_data(image)
    import shutil

    timestr = time.strftime("%Y%m%d-%H%M%S")

  
    src = 'static/animated_gifs/animated.gif'
    dst = 'static/animated_gifs/animated' + timestr + '.gif'
    # 2nd option
    shutil.copy(src, dst) 
    # Return a template that displays the GIF
    return render_template("make_animation.html", gif_filename=gif_filename)

@app.route('/clean_images', methods=['POST'])
def clean_images_route():
    clean_images()
    app.logger.error('line 210 clean_images_route')
    return redirect(url_for('index'))

@app.route('/get_gallery')
def get_gallery():
    image_dir = '/home/jack/Desktop/FLASK/static/images/uploads'
    image_names = os.listdir(image_dir)
    return render_template('get_gallery.html', image_names=image_names)

@app.route('/uploads/<filename>')
def send_image(filename):
    return send_from_directory('static/images/uploads', filename)

@app.route('/uploads/thumbnails/<filename>')
def send_image_thumb(filename):
    return send_from_directory('static/images/uploads/thumbnails', filename)
@app.route('/flask_info')
def flask_info():
    return render_template('flask_info.html')

if __name__ == '__main__':
    app.run(debug=True)


