from flask import Flask, jsonify
import os

app = Flask(__name__)

# Assuming you have a directory named 'stored_files'
stored_files_dir = './stored_files'

@app.route('/list', methods=['GET'])
def get_filenames():
    try:
        filenames = [f for f in os.listdir(stored_files_dir) if os.path.isfile(os.path.join(stored_files_dir, f))]
        return jsonify({'filenames': filenames})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
