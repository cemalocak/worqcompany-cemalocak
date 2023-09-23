from django.shortcuts import redirect
from django.views.generic import TemplateView
from scrap.models import Merchant, Trendyol_Product
from django.views.decorators.csrf import csrf_exempt
from bs4 import BeautifulSoup	
import requests
import json


@csrf_exempt
def find_product(request):
	if request.method == 'POST':
		url = request.POST['url']
		r = requests.get(url)
		source = BeautifulSoup(r.content,"lxml")
		
		# Ürün ve Satıcı Bilgilerinin Alınması	
		data = source.findAll("script", {"type":"application/javascript"})
		data_source = None
		data_json = None
		for i in data:
			if "window.__PRODUCT_DETAIL_APP_INITIAL_STATE__" in i.text:
				data_source = i.text.replace("\n","").replace("window.__PRODUCT_DETAIL_APP_INITIAL_STATE__","")
				data_source = data_source[data_source.find("=")+1:]
				data_source = data_source[:data_source.find("window.TYPageName")]
				data_source = data_source[:data_source.rfind(";")]
				break
		try:
			data_json = json.loads(data_source)


			#Satıcı Bilgilerinin Kaydedilmesi
			merchant_name = data_json['product']['merchant']['name']
			merchant_city = data_json['product']['merchant']['cityName']
			merchant_seller_score = data_json['product']['merchant']['sellerScore']

			product_merchant = Merchant(name=merchant_name, city_name=merchant_city, seller_score=merchant_seller_score)
			product_merchant.save()

			#Diğer Satıcı Bilgilerinin Kaydedilmesi
			other_merchants = []
			for merchant in data_json['product']['otherMerchants']:
				name = merchant['merchant']['name']
				city = merchant['merchant']['cityName']
				seller_score = merchant['merchant']['sellerScore']
				other_merchant = Merchant(name=name, city_name=city, seller_score=seller_score)
				other_merchant.save()
				other_merchants.append(other_merchant)



			product_name = data_json['product']['name']
			product_brand = data_json['product']['brand']['name']
			product_category = data_json['product']['category']['hierarchy']
			product_sellingPrice = data_json['product']['price']['sellingPrice']['value']
			product_discountedPrice = data_json['product']['price']['discountedPrice']['value']

			product = Trendyol_Product(
				name=product_name, 
				brand=product_brand, 
				sellingPrice=product_sellingPrice, 
				discountedPrice=product_discountedPrice, 
				category=product_category, 
				merchant=product_merchant,
				url = url
				)
			product.save()
			product.other_merchants.set(other_merchants)
			product.save()
			return redirect('index')
		except Exception as e:
			print(e)
			print("\n")
			print(data_source)
			return redirect('index')
	



class Main_Page(TemplateView):
	template_name = 'index.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		products = Trendyol_Product.objects.all()
		context['products'] = products
		return context



class Product_Detail(TemplateView):
	template_name = 'product_detail.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		product = Trendyol_Product.objects.get(pk=self.kwargs['pk'])
		context['product'] = product
		return context
	
def Product_Delete(request, pk):
	product = Trendyol_Product.objects.get(pk=pk)
	product.delete()
	return redirect('index')