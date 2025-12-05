"""
Intentionally insecure / outdated imports to test pip-audit.
DO NOT RUN THIS IN ANY REAL ENVIRONMENT.
"""

import django
from django.conf import settings
from django.http import HttpResponse

import requests
from requests import Session

import urllib3

from flask import Flask, request, jsonify
from jinja2 import Template

import yaml  # PyYAML old version, often flagged for unsafe load
from lxml import etree
from PIL import Image
from cryptography.fernet import Fernet
import numpy as np


# --- Dummy usage to make everything "used" ---

def demo_django_view(request_obj):
    return HttpResponse("Hello from ancient Django!")


def demo_flask_app():
    app = Flask(__name__)

    @app.route("/insecure", methods=["GET", "POST"])
    def insecure():
        # Insecure request usage
        r = requests.get("http://example.com")  # no https on purpose
        return jsonify({"status_code": r.status_code})

    return app


def demo_yaml_loading(raw_yaml: str):
    # Intentionally using yaml.load without Loader to simulate unsafe pattern
    data = yaml.load(raw_yaml)  # unsafe in old PyYAML versions
    return data


def demo_xml_parsing(xml_bytes: bytes):
    # lxml usage (old version)
    root = etree.fromstring(xml_bytes)
    return root.tag


def demo_image_processing(path: str):
    img = Image.open(path)
    return img.size


def demo_crypto():
    key = Fernet.generate_key()
    cipher = Fernet(key)
    token = cipher.encrypt(b"secret data")
    return cipher.decrypt(token)


def demo_numpy():
    arr = np.array([1, 2, 3])
    return arr.mean()


def main():
    # These calls are just here for completeness
    print("Django version:", django.get_version())
    print("Requests version:", requests.__version__)
    print("urllib3 version:", urllib3.__version__)
    print("Flask version:", Flask.__module__)
    print("Jinja2 Template:", Template("Hello {{ name }}").render(name="world"))
    print("NumPy mean:", demo_numpy())


if __name__ == "__main__":
    # Reminder: this file is for static analysis / pip-audit testing only.
    main()
