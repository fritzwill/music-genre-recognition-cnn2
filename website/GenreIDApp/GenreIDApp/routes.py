from flask import render_template
from GenreIDApp import app

from GenreIDApp.process_vote import process_mp3, MP3S_FOLDER

import os
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename


UPLOAD_FOLDER = '/home/group/uploads'
# UPLOAD_FOLDER = './static/processing/mp3s'


ALLOWED_EXTENSIONS = set(['mp3'])

app.config['UPLOAD_FOLDER'] = MP3S_FOLDER

# TODO: add to individual functions
# this works as long as 'apache' is the group of the created folders
# try:
#     os.mkdir(app.config['UPLOAD_FOLDER'])
# except FileExistsError:
#     pass


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Thomas'}
    return render_template('index.html', title='Home', user=user)

@app.route('/landing')
def landing():
    return render_template('landing.html')

@app.route('/upload-view', methods=['GET', 'POST'])
def upload_file_view():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            mp3_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(mp3_file_path)
            return redirect(url_for('uploaded_file',
                                    filename=filename))
    return render_template("upload.html")


@app.route('/upload', methods=['GET', 'POST'])
@app.route('/upload-analyze', methods=['GET', 'POST'])
def upload_file_analyze():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            mp3_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(mp3_file_path)

            genre, spectro_path_full, confidence = process_mp3(mp3_file_path)
            spectro_path = '/'.join(spectro_path_full.split('/')[5:])
            base_name = os.path.basename(mp3_file_path)

            payload = {'genre': genre, 'spectro_path': spectro_path, 'name': base_name, 'confidence': confidence}

            return render_template("result.html", song=payload)

    return render_template("upload.html")

from flask import send_from_directory

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

