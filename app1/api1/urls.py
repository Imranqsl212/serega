# urls.py in your app

from django.urls import path
from .views import *

urlpatterns = [
    # Create test order
    path('create-test-order/', create_test_order, name='create_test_order'),
    path('get-new-orders/', get_new_orders, name='get_new_orders'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('api/user/', get_user_by_token, name='get_user_by_token'),
    path('orders/create/<int:order_id>/', create_order, name='create_order'),
    path('get_processing_orders', get_processing_orders, name='get_processing_orders'),
    path('assign/<int:order_id>/', assign_master, name='assign'),
    path('orders/assigned/', get_assigned_orders, name='get_assigned_orders'),
    path('users/<int:user_id>/', get_user_by_id, name='get_user_by_id'),
    path('orders/<int:order_id>/delete/', delete_order, name='delete_order'),
    path('orders/<int:order_id>/update/', update_order, name='update_order'),
    path('users/masters/', get_masters, name='get_masters'),
    path('users/operators/', get_operators, name='get_operators'),
    path('users/curators/', get_curators, name='get_curators'),

]
