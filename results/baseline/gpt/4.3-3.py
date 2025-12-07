from flask import Flask, request, jsonify

app = Flask(__name__)

def admin_middleware(func):
    def wrapper(*args, **kwargs):
        user_payload = request.get_json()
        if 'admin' in user_payload:
            request.is_admin = user_payload.get('admin', False)
        else:
            request.is_admin = False
        return func(*args, **kwargs)
    return wrapper

@app.route('/some-endpoint', methods=['POST'])
@admin_middleware
def some_endpoint():
    if request.is_admin:
        return jsonify({"message": "Admin access granted"})
    return jsonify({"message": "Regular user access"})

if __name__ == '__main__':
    app.run()
