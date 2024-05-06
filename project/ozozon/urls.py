from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from .views import ProductsListView, ProductDetail, ProductCreate, profile_view, RegisterView, ConfirmUser, account_inactive

urlpatterns = [
    path('', ProductsListView.as_view(), name='plist'),
    path('<int:pk>', ProductDetail.as_view(), name='detail'),
    path('create/', ProductCreate.as_view(), name='create'),
    path('profile/', profile_view, name='profile'),
    #path('signup/', RegisterView.as_view(), name='register'),
    path('login', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(template_name='registration/logout.html'),
         name='logout'),
    path('inactive/', account_inactive, name="account_inactive"),
    path('confirm/', ConfirmUser.as_view(), name='confirm_user'),
]