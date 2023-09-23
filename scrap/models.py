from django.db import models

class Merchant(models.Model):
	name = models.CharField(max_length=200)
	city_name = models.CharField(max_length=200)
	seller_score = models.DecimalField(max_digits=10, decimal_places=2)

	def __str__(self):
		return self.name
	
	class Meta:
		verbose_name = 'Satıcı'
		verbose_name_plural = 'Satıcılar'

class Trendyol_Product(models.Model):
	name = models.CharField(max_length=200)
	brand = models.CharField(max_length=200)
	sellingPrice = models.DecimalField(max_digits=10, decimal_places=2)
	discountedPrice = models.DecimalField(max_digits=10, decimal_places=2)
	category = models.CharField(max_length=200)
	merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE)
	other_merchants = models.ManyToManyField(Merchant, related_name='other_Merchants')
	url = models.CharField(max_length=200)

	def __str__(self):
		return self.name
	
	class Meta:
		verbose_name = 'Ürün'
		verbose_name_plural = 'Ürünler'