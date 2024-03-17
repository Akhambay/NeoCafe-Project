from django.http import Http404
from rest_framework import generics
from drf_spectacular.utils import extend_schema
from .models import Order, Table
from users.models import WaiterProfile, CustomerProfile, Profile
from .serializers import OrderSerializer, CustomerOrderSerializer, OrderOnlineSerializer, TableSerializer, TableDetailedSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.utils import timezone


class OrderView(APIView):
    permission_classes = [IsAuthenticated]

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

            if hasattr(request.user, 'profile'):
                order.employee = request.user.profile
                order.save()
                return Response({'data': 'OK'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': 'User profile does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderOnlineView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        orders = Order.objects.filter(customer=request.user)
        serializer = OrderOnlineSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        # Add the customer field to the data
        data['customer'] = request.user.pk

        serializer = OrderOnlineSerializer(
            data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({'data': 'OK'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    description="List all orders or create a new order",
    summary="List and Create Orders",
    responses={200: OrderSerializer(many=True)}
)
class OrderListView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    # permission_classes = [IsAuthenticated]


@extend_schema(
    description="List all online orders",
    summary="List online Orders",
    responses={200: OrderOnlineSerializer(many=True)}
)
class OrderOnlineListView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderOnlineSerializer
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


class TableCreateView(generics.CreateAPIView):
    queryset = Table.objects.all()
    serializer_class = TableSerializer


class TableListView(generics.ListAPIView):
    serializer_class = TableSerializer

    def get_queryset(self):
        branch_id = self.kwargs['branch_id']
        return Table.objects.filter(branch_id=branch_id)


class TableView(APIView):

    def get(self, request, *args, **kwargs):
        tables = Table.objects.all()
        serializer = TableSerializer(tables, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = TableSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'data': 'OK'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors)


class TableDetailedView(APIView):

    def get(self, request, *args, **kwargs):
        try:
            table = Table.objects.get(table_number=kwargs['table_number'])
        except Table.DoesNotExist:
            return Response({'data': 'Table not found'}, status.HTTP_404_NOT_FOUND)
        serializer = TableDetailedSerializer(table)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = TableDetailedSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'data': 'OK'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors)
