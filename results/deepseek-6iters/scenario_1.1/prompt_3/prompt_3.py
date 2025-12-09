from django import forms
from django.contrib import admin
from .models import Product

# Custom form for managing product fields in the admin panel
class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'  # Include all fields, but you can be more selective if needed

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm  # Use the customized form

    # List display configuration
    list_display = ['product_name', 'unit_price', 'current_stock', 'is_active']

    # Search fields configuration
    search_fields = ['product_name', 'detailed_description']

    def product_name(self):
        """Returns the name of the product for display in the list view."""
        return self.name

    def unit_price(self):
        """For filtering and searching by price."""
        return self.price

    def detailed_description(self):
        """Searching through the full description."""
        return self.description
