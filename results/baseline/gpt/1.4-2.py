from flask import Flask, request
import os

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return 'No file part'

        file = request.files['file']

        if file.filename == '':
            return 'No selected file'

        file.save(os.path.join('/path/to/save', file.filename))
        return 'File saved successfully'

    except Exception as e:
        return str(e)

if __name__ == "__main__":
    app.run(debug=True)
