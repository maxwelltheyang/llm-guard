from flask import Flask, request, render_template_string

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload():
    image = request.files['image']
    caption = request.form['caption']
    # Save the image and update the caption in your database or storage
    return "Image uploaded successfully!"

if __name__ == '__main__':
    app.run(debug=True)
