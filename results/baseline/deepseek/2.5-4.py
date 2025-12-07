from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/calc', methods=['POST'])
def calc():
    data = request.get_json()
    try:
        result = eval(data['expression'])
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
