from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

# configure uploads folder
UPLOAD_FOLDER = '/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/edit-caption', methods=['POST'])
def edit_caption():
    image_id = request.form.get('image_id')
    new_caption = request.form.get('new_caption')

    # get the file from the database or storage
    image_file = get_image_from_db(image_id)

    if image_file:
        # save the new caption to the image metadata
        update_image_metadata(image_id, {'caption': new_caption})

        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Image not found'}), 404

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    filename = secure_filename(file.filename)
    image_id = str(len(os.listdir(app.config['UPLOAD_FOLDER'])))

    # save the file to disk
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_id))

    return jsonify({'image_id': image_id})

if __name__ == '__main__':
    app.run(debug=True)
