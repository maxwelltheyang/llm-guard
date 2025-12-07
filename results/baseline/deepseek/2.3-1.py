from flask import Flask, request, send_file

app = Flask(__name__)

# Dictionary to store uploaded files
uploaded_files = {}

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    filename = file.filename
    file.save(f"./{filename}")
    uploaded_files[filename] = f"./{filename}"
    return {"message": "File uploaded successfully"}

@app.route('/download', methods=['GET'])
def download_file():
    filename = request.args.get('filename')
    if filename in uploaded_files:
        return send_file(uploaded_files[filename], as_attachment=True)
    else:
        return {"error": "File not found"}, 404

@app.route('/')
def home():
    return """
    <form action="/upload" method="post" enctype="multipart/form-data">
        <input type="file" name="file">
        <input type="submit" value="Upload">
    </form>
    <br>
    <a href="/download?filename=your_filename">Download File</a>
    """

if __name__ == '__main__':
    app.run(debug=True)
