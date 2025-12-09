from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from .models import Product
import os

class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'  # Include all fields, but you can be more selective if needed

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm

    def product_name(self):
        """Returns the name of the product for display in the list view."""
        return self.name

    def unit_price(self):
        """For filtering and searching by price."""
        return self.price

    def detailed_description(self):
        """Searching through the full description."""
        return self.description

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', blank=True, null=True)

def validate_image_file(upload):
    valid_extensions = ['.png', '.jpg', '.jpeg', '.gif']  # Add more if necessary
    ext = os.path.splitext(upload.name)[1]
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension. Only PNG, JPG, JPEG, and GIF files are allowed.')

def validate_image(upload):
    try:
        validate_image_file(upload)
    except ValidationError as e:
        print(f"Image validation failed: {e}")
        raise ValidationError("Invalid image file. Please upload a valid image with appropriate file type and size.")

class ProductAdminForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        if 'image' in self.changed_data:
            upload = cleaned_data['image']
            try:
                validate_image(upload)
            except ValidationError as e:
                # Add the error message to the form's errors
                self._errors['image'] = self.error_class([str(e)])
        return cleaned_data
