# FLASK
## Image Processing Flask APP
Installation:



<code>git clone https://github.com/JupyterJones/FLASK.git</code><br />
<code>cd FLASK</code><br />
<code>python3.8 -m venv flask_venv</code><br />
<code>source flask_venv.bin/activate</code><br />
<code>python -m pip install -r requirements.txt</code><br />
<code>python app.py</code><br /><br />

This is a Python Image Processing Flask web application. The application seems to have an endpoint to display an index page, an endpoint to display an upload form, an endpoint to upload a file and process it, an endpoint to blend images, and an endpoint to blend an image and audio together.

This code is a Flask application that defines various routes for image processing. It includes the ability to upload an image, process it using a mask,
and blend it with another image. It also has a route that randomly selects an image and displays it on the home page. There are also routes for processing
images using Pygame and converting an image to a video. Additionally, there are several libraries used in the code, including subprocess, logging, and PIL.

The index endpoint randomly selects an image from a directory and displays it on the page.

The upload endpoint allows the user to upload an image and checks if the file is allowed based on the file extension. If the file is allowed, the file is saved to the server and the user is redirected to a page that displays the filename.

The process_images endpoint accepts three images and composites them together based on a binary mask image. The resulting image is saved to a file and returned as a response.

The blend_pil endpoint accepts two images and blends them together using the Python Imaging Library (PIL). The resulting image is saved to a file and returned as a response.

The blend_video endpoint accepts an image and an audio file, blends them together using the moviepy library, and saves the resulting video file to the server. The video file is then displayed on a page.



