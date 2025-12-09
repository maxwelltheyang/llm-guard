from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from .models import Product
import os

def validate_image_file(upload):
    valid_extensions = ['.png', '.jpg', '.jpeg', '.gif']  # Add more if necessary
    ext = os.path.splitext(upload.name)[1]
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension. Please upload a file with one of the following extensions: ' + ', '.join(valid_extensions))

def validate_image(upload):
    try:
        validate_image_file(upload)
    except ValidationError as e:
        print(f"Image validation failed: {e}")
        raise ValidationError("Invalid image file. Please upload a valid image with an appropriate file type and size.")

class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'  # Include all fields, but you can be more selective if needed

    def clean(self):
        cleaned_data = super().clean()
        if 'image' in self.changed_data:  # Check only updated fields to avoid redundant checks
            upload = cleaned_data.get('image')
            if upload:
                try:
                    validate_image(upload)
                except ValidationError as e:
                    self._errors['image'] = self.error_class([str(e)])
        return cleaned_data

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
