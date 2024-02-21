from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from drf_spectacular.utils import extend_schema
from .models import Order
from .serializers import OrderSerializer
from .serializers import CustomerOrderSerializer


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

# ================================================================


class InVenueOrderView(APIView):
    def get(self, request, *args, **kwargs):
        # Retrieve in-venue orders
        invenue_orders = Order.objects.filter(
            order_type=Order.OrderType.IN_VENUE)
        serializer = OrderSerializer(invenue_orders, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        # Create a new in-venue order
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(order_type=Order.OrderType.IN_VENUE)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TakeawayOrderView(APIView):
    def get(self, request, *args, **kwargs):
        # Retrieve takeaway orders
        takeaway_orders = Order.objects.filter(
            order_type=Order.OrderType.TAKEAWAY)
        serializer = OrderSerializer(takeaway_orders, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        # Create a new takeaway order
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(order_type=Order.OrderType.TAKEAWAY)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
