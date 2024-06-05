from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from .views import ProductsListView, ProductDetail, ProductCreate, ProfileView, ProductDeleteView, ConfirmUser, \
    account_inactive, ProductUpdateView, CartView, add_to_cart, remove_from_cart

urlpatterns = [
    path('', ProductsListView.as_view(), name='plist'),
    path('<int:pk>/', ProductDetail.as_view(), name='detail'),
    path('create/', ProductCreate.as_view(), name='create'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('delete/<int:pk>/', ProductDeleteView.as_view(), name='delete'),
    #path('signup/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(template_name='registration/logout.html'),
         name='logout'),
    path('inactive/', account_inactive, name="account_inactive"),
    path('confirm/', ConfirmUser.as_view(), name='confirm_user'),
    path('update/<int:pk>/', ProductUpdateView.as_view(), name='update'),
    path('cart/', CartView.as_view(), name='mycart'),
    path('addtocart/<int:product_id>', add_to_cart, name='addtocart'),
    path('removefromcart/<int:cart_id>', remove_from_cart, name='removefromcart'),

]