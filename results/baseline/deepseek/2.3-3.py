from flask import Flask, jsonify
import os

app = Flask(__name__)

# Example function to return a list of filenames in a directory
@app.route('/list', methods=['GET'])
def get_file_list():
    # Specify the directory you want to list files from
    directory = 'path/to/your/directory'
    try:
        files = os.listdir(directory)
        return jsonify(files)
    except FileNotFoundError:
        return jsonify({'error': 'Directory not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
