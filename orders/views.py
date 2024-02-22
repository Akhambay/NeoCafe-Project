from rest_framework import generics
from drf_spectacular.utils import extend_schema
from .models import Order
from .serializers import OrderSerializer
from .serializers import CustomerOrderSerializer
from rest_framework.permissions import IsAuthenticated


@extend_schema(
    description="Create a new order",
    summary="Create Order",
    responses={200: OrderSerializer(many=False)}
)
class OrderCreateView(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    # permission_classes = [IsAuthenticated]


@extend_schema(
    description="List all orders or create a new order",
    summary="List and Create Orders",
    responses={200: OrderSerializer(many=True)}
)
class OrderListCreateView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    # permission_classes = [IsAuthenticated]


@extend_schema(
    description="Retrieve, update, or delete an order",
    summary="Retrieve, Update, Delete Order",
    responses={200: OrderSerializer(many=False)}
)
class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    # permission_classes = [IsAuthenticated]


@extend_schema(
    description="Retrieve customer order history",
    summary="Customer Order History",
    responses={200: CustomerOrderSerializer(many=True)}
)
class CustomerOrderHistoryView(generics.ListAPIView):
    serializer_class = CustomerOrderSerializer

    def get_queryset(self):
        customer = self.request.user
        return Order.objects.filter(customer=customer)
