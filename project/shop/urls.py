from django.urls import path
from . import views

app_name = 'shop'


urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('product/<slug:product_slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('category/<slug:category_slug>/', views.CategoryProductsView.as_view(), name='category_products'),
    path('search/', views.search_products, name='search'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:cart_item_id>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('cart/', views.cart_view, name='cart'),
]