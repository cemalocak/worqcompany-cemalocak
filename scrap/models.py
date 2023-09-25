import json
from django.db import models
from bs4 import BeautifulSoup	
import requests
import logging

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
	
	def get_product_data(self):
		r = requests.get(self.url)
		source = BeautifulSoup(r.content,"lxml")
		
		#Ürün bilgilerini içeren script tag'inin bulunması
		data = source.findAll("script", {"type":"application/javascript"})

		#Script tag'inin içindeki verinin alınması
		for i in data:
			if "window.__PRODUCT_DETAIL_APP_INITIAL_STATE__" in i.text:
				data_source = i.text.replace("\n","").replace("window.__PRODUCT_DETAIL_APP_INITIAL_STATE__","")
				data_source = data_source[data_source.find("=")+1:]
				data_source = data_source[:data_source.find("window.TYPageName")]
				data_source = data_source[:data_source.rfind(";")]
				break
		try:
			#ilgili verinin json formatına çevrilmesi
			return json.loads(data_source)
		except Exception as e:
			logging.error(e)
			return False

	
	class Meta:
		verbose_name = 'Ürün'
		verbose_name_plural = 'Ürünler'