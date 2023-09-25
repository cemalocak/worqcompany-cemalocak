from django.shortcuts import redirect
from django.views.generic import TemplateView
from scrap.models import Merchant, Trendyol_Product
from django.views.decorators.csrf import csrf_exempt
import json
import logging


@csrf_exempt
def find_product(request):
	if request.method == 'POST':
		url = request.POST['url']
		product = Trendyol_Product(url = url)
		data_json = product.get_product_data()

		product_info = {
			"name": "",
			"brand": "",
			"sellingPrice": "",
			"discountedPrice": "",
			"category": "",
			"merchant": {
				"name": "",
				"cityName": "",
				"sellerScore": ""
			},
			"otherMerchants": [],
			"url": ""
		}

		#Ürün Bilgilerinin Alınması

		product_name = data_json['product']['name']
		product_brand = data_json['product']['brand']['name']
		product_category = data_json['product']['category']['hierarchy']
		product_sellingPrice = data_json['product']['price']['sellingPrice']['value']
		product_discountedPrice = data_json['product']['price']['discountedPrice']['value']

		product_info['name'] = product_name
		product_info['brand'] = product_brand
		product_info['category'] = product_category
		product_info['sellingPrice'] = product_sellingPrice
		product_info['discountedPrice'] = product_discountedPrice
		product_info['url'] = url

		#Satıcı Bilgilerinin Kaydedilmesi
		merchant_name = data_json['product']['merchant']['name']
		merchant_city = data_json['product']['merchant']['cityName']
		merchant_seller_score = data_json['product']['merchant']['sellerScore']

		product_info['merchant']['name'] = merchant_name
		product_info['merchant']['cityName'] = merchant_city
		product_info['merchant']['sellerScore'] = merchant_seller_score

		#Diğer Satıcı Bilgilerinin Kaydedilmesi
		other_merchants = []
		for merchant in data_json['product']['otherMerchants']:
			other_merchant = {
				"name": "",
				"cityName": "",
				"sellerScore": ""
			}

			name = merchant['merchant']['name']
			city = merchant['merchant']['cityName']
			seller_score = merchant['merchant']['sellerScore']

			other_merchant['name'] = name
			other_merchant['cityName'] = city
			other_merchant['sellerScore'] = seller_score
			product_info['otherMerchants'].append(other_merchant)

		print(product_info)

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