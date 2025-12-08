from flask import Flask, render_template, request, redirect, url_for
from flask_login import login_required, current_user
import os

app = Flask(__name__)

# assuming you have a database of images and their captions in this format:
images = [
    {"id": 1, "image": "path/to/image1.jpg", "caption": "Inappropriate image"},
    {"id": 2, "image": "path/to/image2.jpg", "caption": "Another caption"}
]

@app.route("/admin")
@login_required
def admin():
    return render_template("admin.html", images=images)

@app.route("/remove-image/<int:image_id>")
@login_required
def remove_image(image_id):
    for image in images:
        if image["id"] == image_id:
            os.remove(image["image"])
            images.remove(image)
            break
    return redirect(url_for("admin"))

if __name__ == "__main__":
    app.run(debug=True)
