from django.contrib import admin

from scrap.models import Merchant, Trendyol_Product

@admin.register(Trendyol_Product)
class Trendyol_Product_Admin(admin.ModelAdmin):
	list_display = ('name', 'brand', 'sellingPrice', 'discountedPrice', 'category', 'merchant')
	list_filter = ('brand', 'category', 'merchant')
	search_fields = ('name', 'brand', 'category', 'merchant')
	list_per_page = 20
	ordering = ['-id']

@admin.register(Merchant)
class Merchant_Admin(admin.ModelAdmin):
	list_display = ('name', 'city_name', 'seller_score')
	list_filter = ("name", 'city_name')
	search_fields = ('name', 'city_name')
	list_per_page = 20
	ordering = ['-id']