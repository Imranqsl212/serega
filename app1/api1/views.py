from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from .models import Order, CustomUser, IsOperator, IsCurator, IsMaster
from .serializers import OrderSerializer


# Create test order
@api_view(['POST'])
def create_test_order(request):
    serializer = OrderSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

@api_view(['GET'])
@permission_classes([IsOperator])
def get_new_orders(request):
    orders = Order.objects.filter(status='новый')
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


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
