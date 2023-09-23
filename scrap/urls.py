from django.urls import path
from scrap import views

urlpatterns = [
	 path('', views.Main_Page.as_view(), name='index'),
	 path('find_product/', views.find_product, name='find_product'),
	 path('product-detail/<int:pk>/', views.Product_Detail.as_view(), name='product_detail'),
	 path('product-delete/<int:pk>/', views.Product_Delete, name='product_de'),

	]