from flask import Flask, jsonify

app = Flask(__name__)

# Simulated storage of filenames
filenames = ['file1.txt', 'file2.txt', 'file3.txt']

@app.route('/list', methods=['GET'])
def list_files():
    return jsonify(filenames)

if __name__ == '__main__':
    app.run(debug=True)
