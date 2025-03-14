from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from .models import Order, CustomUser, IsOperator, IsCurator, IsMaster
from .serializers import OrderSerializer, CustomUserSerializer


# Create test order
@api_view(['POST'])
def create_test_order(request):
    serializer = OrderSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

@api_view(['GET'])
# @permission_classes([IsOperator])
def get_new_orders(request):
    orders = Order.objects.filter(status='новый')
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

@api_view(['POST'])
# @permission_classes([IsOperator])
def create_order(request):
    serializer = OrderSerializer(data=request.data)
    if serializer.is_valid():
        order = serializer.save(operator=request.user, status='в обработке')
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        # Authenticate the user using email and password
        user = authenticate(email=email, password=password)

        if user is not None:
            # Generate the token for the authenticated user
            token, created = Token.objects.get_or_create(user=user)
            return Response(
                {
                    "token": token.key,  # Send back the token
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "role": user.role,
                    },
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_user_by_token(request):
    user = request.user
    serializer = CustomUserSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)




@api_view(['GET'])
# @permission_classes([IsCurator])
def get_processing_orders(request):
    orders = Order.objects.filter(status='в обработке')
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(['PATCH'])
# @permission_classes([IsCurator])
def assign_master(request, order_id):
    try:
        order = Order.objects.get(id=order_id, status='в обработке')
    except Order.DoesNotExist:
        return Response({'error': 'Order not found or not in processing state'}, status=status.HTTP_404_NOT_FOUND)

    master_id = request.data.get('assigned_master')
    if not master_id:
        return Response({'error': 'Master ID is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        master = CustomUser.objects.get(id=master_id, role='master')
    except CustomUser.DoesNotExist:
        return Response({'error': 'Invalid master ID'}, status=status.HTTP_400_BAD_REQUEST)

    order.assigned_master = master
    order.status = 'назначен'
    order.save()

    return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)


@api_view(['GET'])
# @permission_classes([IsMaster])
def get_assigned_orders(request):
    orders = Order.objects.filter(assigned_master=request.user)
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)



