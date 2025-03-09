# urls.py in your app

from django.urls import path
from .views import *

urlpatterns = [
    # Create test order
    path('create-test-order/', create_test_order, name='create_test_order'),

    # Get new orders (only for operator)
    path('get-new-orders/', get_new_orders, name='get_new_orders'),
    path('login/', LoginAPIView.as_view(), name='login'),

]
