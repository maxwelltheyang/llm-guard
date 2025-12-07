import json
from flask import request, jsonify

class FileUploader:
    def __init__(self):
        self.metadata_store = {}

    def upload_file(self, file, metadata=None):
        if metadata is not None:
            try:
                json.loads(metadata)
            except json.JSONDecodeError:
                return "Invalid JSON metadata", 400
            self.metadata_store[file.filename] = metadata

        return jsonify({'message': f'File uploaded successfully: {file.filename}'}), 201

    def get_metadata(self, filename):
        if filename in self.metadata_store:
            return jsonify({'metadata': json.loads(self.metadata_store[filename])}), 200
        else:
            return "No metadata found for this file", 404
