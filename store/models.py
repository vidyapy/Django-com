# store/models.py
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User # Or your custom user model if you define one later

# Ensure Category is defined before Product, as Product uses Category
class Category(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, unique=True) # For clean URLs

    class Meta:
        ordering = ('name',)
        verbose_name = 'category'
        verbose_name_plural = 'categories'
        # No 'indexes' needed here unless you have specific indexing requirements for Category itself

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        # Assumes a URL pattern named 'store:product_list_by_category'
        return reverse('store:product_list_by_category', args=[self.slug])


class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, db_index=True)
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('name',)
        # --- CORRECTED: Replaced 'index_together' with 'indexes' ---
        indexes = [
            models.Index(fields=['id', 'slug']),
            # You can add more indexes here if needed, e.g.,
            # models.Index(fields=['name']),
            # models.Index(fields=['category', 'available']),
        ]
        verbose_name = 'product'
        verbose_name_plural = 'products' # Recommended for clarity in admin

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        # Assumes a URL pattern named 'store:product_detail'
        return reverse('store:product_detail', args=[self.id, self.slug])


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    address = models.CharField(max_length=250)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False) # For dummy payment

    class Meta:
        ordering = ('-created',)
        verbose_name = 'order'
        verbose_name_plural = 'orders' # Recommended for clarity in admin

    def __str__(self):
        return f'Order {self.id}'

    def get_total_cost(self):
        # Sums the cost of all related order items
        # 'items' is the related_name from OrderItem's ForeignKey to Order
        return sum(item.get_cost() for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        # You might want to add ordering here, e.g., by product name or id
        ordering = ('product__name',) # Orders items within an order by product name
        verbose_name = 'order item'
        verbose_name_plural = 'order items' # Recommended for clarity in admin

    def __str__(self):
        return f'{self.id}' # Or more descriptive: f'{self.product.name} ({self.quantity})'

    def get_cost(self):
        return self.price * self.quantity