from rest_framework import generics
from drf_spectacular.utils import extend_schema
from .models import Order, Table
from users.models import WaiterProfile, CustomerProfile
from .serializers import OrderSerializer
from .serializers import CustomerOrderSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from users.models import WaiterProfile, CustomerProfile
from rest_framework.views import APIView
from django.utils import timezone


class OrderView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            order_id = serializer.data.get('id')
            order = Order.objects.get(id=order_id)
            order.employee = request.user.waiterprofile
            order.save()
            return Response({'data': 'OK'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors)


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


class ModifyOrderView(APIView):

    def put(self, request, *args, **kwargs):
        order = Order.objects.get(id=kwargs['order_id'])
        order_minute, order_hour = order.date_created.minute, order.date_created.hour * 60
        current_minute, current_hour = timezone.now().minute, timezone.now().hour * 60
        order_time = order_minute + order_hour
        current_time = current_minute + current_hour
        abs_value = abs(order_time - current_time)
        serializer = OrderSerializer(order, data=request.data)
        if serializer.is_valid():
            if abs_value <= 5 and order.status == 'In progress':
                serializer.save()
                # order_id = serializer.data.get('id') my homework
                # count_order(order_id)
                return Response({'data': 'order updated success'})
            return Response({'data': f'time is up or order is {order.status}'})
        return Response(serializer.errors)

    def delete(self, request, *args, **kwargs):
        order = Order.objects.get(id=kwargs['order_id'])
        order_minute, order_hour = order.date_created.minute, order.date_created.hour * 60
        current_minute, current_hour = timezone.now().minute, timezone.now().hour * 60
        order_time = order_minute + order_hour
        current_time = current_minute + current_hour
        abs_value = abs(order_time - current_time)
        if abs_value <= 5 and order.status == 'in process':
            order.delete()
            return Response({'data': 'order is canceled'})
        return Response({'data': f'time is up or order is {order.status}'})


class OrderCreateView(generics.CreateAPIView):
    def get(self, request, *args, **kwargs):
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            order_id = serializer.data.get('id')
            try:
                profile = WaiterProfile.objects.get(user=request.user)
            except WaiterProfile.DoesNotExist:
                profile = CustomerProfile.objects.get(user=request.user)

            if isinstance(profile, WaiterProfile):
                order = Order.objects.get(id=order_id)
                order.employee = request.user.employeeprofile
                order.save()

            return Response({'data': 'OK'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors)
