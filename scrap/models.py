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
	
	#save_from_json methodu, ilgili ürünün satıcısını kaydeder
	def save_from_json(self, data_json):
		try:
			self.name = data_json['product']['merchant']['name']
		except KeyError as e:
			logging.error(f"'Satıcı İsmi' bulunamadı veya geçersiz: {e}")
			self.name = "Satıcı Adı Bulunamadı"
		
		try:
			self.city_name = data_json['product']['merchant']['cityName']
		except KeyError as e:
			logging.error(f"'Satıcı Şehri' bulunamadı veya geçersiz: {e}")
			self.city_name = "Şehir Adı Bulunamadı"
		
		try:
			self.seller_score = data_json['product']['merchant']['sellerScore']
		except KeyError as e:
			logging.error(f"'Satıcı Puanı' bulunamadı veya geçersiz: {e}")
			self.seller_score = 0

		self.save()
		return self
	
	#save_other_merchants_from_json methodu, ilgili ürünün diğer satıcılarını kaydeder
	def save_other_merchants_from_json(self, data_json):
		other_merchants = []
		try:
			merchant_data_json = data_json['product']['otherMerchants']
		except KeyError as e:
			logging.error(f"'Diğer Satıcılar' bulunamadı veya geçersiz: {e}")
			return other_merchants

		for merchant in merchant_data_json:
			other_merchant = Merchant()
			try:
				other_merchant.name = merchant['merchant']['name']
			except KeyError as e:
				logging.error(f"'Satıcı İsmi' bulunamadı veya geçersiz: {e}")
				other_merchant.name = "Satıcı Adı Bulunamadı"

			try:
				other_merchant.city_name = merchant['merchant']['cityName']
			except KeyError as e:
				logging.error(f"'Satıcı Şehri' bulunamadı veya geçersiz: {e}")
				other_merchant.city_name = "Şehir Adı Bulunamadı"

			try:
				other_merchant.seller_score = merchant['merchant']['sellerScore']
			except KeyError as e:
				logging.error(f"'Satıcı Puanı' bulunamadı veya geçersiz: {e}")
				other_merchant.seller_score = 0

			other_merchant.save()
			other_merchants.append(other_merchant)
		return other_merchants
			
	
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
	
	#get_product_data methodu, ilgili ürünün bilgilerini JSON formatında return eder
	def get_product_data(self):
		r = requests.get(self.url)
		source = BeautifulSoup(r.content,"lxml")
		
		#Ürün bilgilerini içeren script tag'inin bulunması
		#Script tag'inin içindeki verinin alınması
		data = source.findAll("script", {"type":"application/javascript"})
		for i in data:
			if "window.__PRODUCT_DETAIL_APP_INITIAL_STATE__" in i.text:
				data_source = i.text.replace("\n","").replace("window.__PRODUCT_DETAIL_APP_INITIAL_STATE__","")
				data_source = data_source[data_source.find("=")+1:]
				data_source = data_source[:data_source.find("window.TYPageName")]
				data_source = data_source[:data_source.rfind(";")]
				break
		try:
			#ilgili verinin json formatına çevrilmesi ve return edilmesi
			return json.loads(data_source)
		except Exception as e:
			logging.error(f"Json formatına çevirme hatası: {e}")
			return False
		

	#save_from_json methodu, ilgili ürünün bilgilerini JSON formatında alır ve ürünü kaydeder
	def save_from_json(self, data_json):
		#Ürün Bilgilerinin Alınması
		try:
			self.name = data_json['product']['name']
		except KeyError as e:
			logging.error(f"'İsim' bulunamadı veya geçersiz: {e}")
			self.name = "Ürün Adı Bulunamadı"
		
		try:
			self.brand = data_json['product']['brand']['name']
		except KeyError as e:
			logging.error(f"'Marka' bulunamadı veya geçersiz: {e}")
			self.brand = "Marka Bulunamadı"

		try:
			self.category = data_json['product']['category']['hierarchy']
		except KeyError as e:
			logging.error(f"'Kategori' bulunamadı veya geçersiz: {e}")
			self.category = "Kategori Bulunamadı"

		try:
			self.sellingPrice = data_json['product']['price']['sellingPrice']['value']
		except KeyError as e:
			logging.error(f"'Liste Fiyatı' bulunamadı veya geçersiz: {e}")
			self.sellingPrice = 0

		try:
			self.discountedPrice = data_json['product']['price']['discountedPrice']['value']
		except KeyError as e:
			logging.error(f"'İndirimli Fiyat' bulunamadı veya geçersiz: {e}")
			self.discountedPrice = 0

		#Satıcı Bilgilerinin Kaydedilmesi
		self.merchant = Merchant().save_from_json(data_json)
		self.save()

		#Diğer Satıcı Bilgilerinin Kaydedilmesi
		other_merchants = Merchant().save_other_merchants_from_json(data_json)
		self.other_merchants.set(other_merchants)
		
		return self

	
	class Meta:
		verbose_name = 'Ürün'
		verbose_name_plural = 'Ürünler'