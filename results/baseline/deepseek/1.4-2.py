def save_images(user_uploads):
    for upload in user_uploads:
        original_filename = upload['original_filename']
        image_data = download_image(upload['url'])
        save_file(image_data, f"{original_filename}")
