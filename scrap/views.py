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
		if data_json != False:
			product.save_from_json(data_json)
			
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