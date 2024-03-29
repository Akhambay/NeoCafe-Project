from .serializers import OrderOnlineSerializer
from .models import Order
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import PermissionDenied
from rest_framework import generics, status
from django.db.models import Count
from menu.models import Menu_Item
from rest_framework.decorators import api_view
from django.http import Http404
from drf_spectacular.utils import extend_schema
from .models import Order, Table
from users.models import WaiterProfile, BartenderProfile, Profile, EmployeeSchedule, CustomerProfile
from .serializers import (OrderSerializer, OrderOnlineSerializer, OrderDetailedSerializer,
                          OrderOnlineDetailedSerializer,
                          TableSerializer, TableDetailedSerializer)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework import status
from django.db import transaction
from users.serializers import CustomUserSerializer


def create_employee_profile(employee, profile_model, schedules_data=None):
    # Create or retrieve profile
    employee_profile, created = profile_model.objects.get_or_create(
        user=employee)

    # Check if the profile was created or already existed
    if created and schedules_data is not None:
        # Create Schedule instances and associate them with the profile
        for schedule_data in schedules_data:
            day = schedule_data['day']
            start_time = schedule_data['start_time']
            end_time = schedule_data['end_time']

            # Create Schedule instance
            schedule_instance = EmployeeSchedule.objects.create(
                day=day, start_time=start_time, end_time=end_time, employee=employee_profile)

    return employee_profile


def create_or_get_employee_profile(user, profile_model):
    try:
        # Check if the user already has a profile
        return profile_model.objects.get(user=user), False
    except profile_model.DoesNotExist:
        # Create a new profile if it doesn't exist
        profile = profile_model.objects.create(user=user)
        return profile, True


class OrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = OrderSerializer(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            with transaction.atomic():
                if request.user.user_type == 'Waiter':
                    profile_model = WaiterProfile
                elif request.user.user_type == 'Bartender':
                    profile_model = BartenderProfile

                # Create or retrieve the profile
                user_profile, profile_created = create_or_get_employee_profile(
                    request.user, profile_model)

                order_id = serializer.data.get('id')
                order = Order.objects.get(id=order_id)

                # Assign the user profile to the order
                if profile_created:
                    # Assuming there's a user field in WaiterProfile
                    custom_user_instance = user_profile.user
                    order.employee = custom_user_instance
                    order.save()
                else:
                    # If the profile already exists, ensure it is associated with the order
                    # Assuming there's a user field in WaiterProfile
                    custom_user_instance = user_profile.user
                    order.employee = custom_user_instance
                    order.save()

                return Response({'data': 'OK'}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    description="Retrieve, update, or delete an order by its ID",
    summary="Retrieve, Update, Delete Order by ID",
    responses={200: OrderDetailedSerializer()}
)
class OrderDetailByIdView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderDetailedSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        order_id = self.kwargs.get('order_id')
        return get_object_or_404(Order, id=order_id)

    def put(self, request, *args, **kwargs):
        order_instance = self.get_object()
        serializer = self.get_serializer(
            order_instance, data=request.data, partial=True)

        if serializer.is_valid():
            # Check if table_number is provided in request data
            new_table_number = request.data.get('table_number')
            if new_table_number is not None:
                # Get the table instance corresponding to the provided table number
                new_table = get_object_or_404(
                    Table, table_number=new_table_number)
                serializer.validated_data['table'] = new_table

            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        order_instance = self.get_object()
        order_instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


def create_or_get_customer_profile(user, profile_model):
    try:
        # Check if the user already has a profile
        return profile_model.objects.get(user=user), False
    except profile_model.DoesNotExist:
        # Create a new profile if it doesn't exist
        profile = profile_model.objects.create(user=user)
        return profile, True


@extend_schema(
    description="Retrieve, update, or delete an order by its ID",
    summary="Retrieve, Update, Delete Order by ID",
    responses={200: OrderDetailedSerializer()}
)
class OrderOnlineDetailByIdView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderOnlineDetailedSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        order_id = self.kwargs.get('order_id')
        return get_object_or_404(Order, id=order_id)

    def put(self, request, *args, **kwargs):
        order_instance = self.get_object()
        serializer = self.get_serializer(
            order_instance, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        order_instance = self.get_object()
        order_instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


def create_or_get_customer_profile(user, profile_model):
    try:
        # Check if the user already has a profile
        return profile_model.objects.get(user=user), False
    except profile_model.DoesNotExist:
        # Create a new profile if it doesn't exist
        profile = profile_model.objects.create(user=user)
        return profile, True


class OrderOnlineView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = OrderOnlineSerializer(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            with transaction.atomic():
                if request.user.user_type == 'Customer':
                    profile_model = CustomerProfile

                    user_profile, profile_created = create_or_get_customer_profile(
                        request.user, profile_model)

                    order_id = serializer.data.get('id')
                    order = Order.objects.get(id=order_id)

                    # Assign the user profile to the order
                    if profile_created:
                        # Assuming there's a user field in CustomerProfile
                        custom_user_instance = user_profile.user
                        order.customer = custom_user_instance
                        order.save()
                    else:
                        # If the profile already exists, ensure it is associated with the order
                        # Assuming there's a user field in CustomerProfile
                        custom_user_instance = user_profile.user
                        order.customer = custom_user_instance
                        order.save()

                return Response({'Online order': 'created'}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    description="List all orders",
    summary="List Orders",
    responses={200: OrderSerializer(many=True)}
)
class OrderListView(generics.ListCreateAPIView):
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderSerializer
    # permission_classes = [IsAuthenticated]


@extend_schema(
    description="List all orders",
    summary="List Orders",
    responses={200: OrderOnlineSerializer(many=True)}
)
class OrderOnlineListView(generics.ListCreateAPIView):
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderOnlineSerializer
    # permission_classes = [IsAuthenticated]


class WaiterOrdersView(APIView):
    """
    View to list orders for a specific branch where the waiter works.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, branch_id):
        if request.user.branch_id == branch_id:
            orders = Order.objects.filter(
                branch_id=branch_id).order_by('-created_at')
            serializer = OrderSerializer(orders, many=True)
            return Response(serializer.data)
        return Response({'error': 'Unauthorized or invalid branch'}, status=status.HTTP_401_UNAUTHORIZED)


class NewOrdersView(APIView):
    """
    View to list new orders for a specific branch where the waiter works.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        description="List new orders for the specific branch where the waiter works.",
        summary="List New Orders",
        responses={200: OrderSerializer(many=True)}
    )
    def get(self, request, branch_id):
        if request.user.branch_id == branch_id:
            orders = Order.objects.filter(
                branch_id=branch_id, order_status='Новый').order_by('-created_at')
            serializer = OrderSerializer(orders, many=True)
            return Response(serializer.data)
        return Response({'error': 'Unauthorized or invalid branch'}, status=status.HTTP_401_UNAUTHORIZED)


class InProgressOrdersListView(generics.ListCreateAPIView):
    """
    List all in progress orders for the branch where the waiter works.
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        description="List all orders with status 'В процессе' for the branch where the waiter works.",
        summary="List Orders with Status 'В процессе'",
        responses={200: OrderSerializer(many=True)}
    )
    def get(self, request, branch_id):
        if request.user.branch_id == branch_id:
            orders = Order.objects.filter(
                branch_id=branch_id, order_status='В процессе').order_by('-created_at')
            serializer = OrderSerializer(orders, many=True)
            return Response(serializer.data)
        return Response({'error': 'Unauthorized or invalid branch'}, status=status.HTTP_401_UNAUTHORIZED)


class ReadyOrdersListView(generics.ListCreateAPIView):
    """
    List all Ready orders for the branch where the waiter works.
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        description="List all orders with status 'Готов' for the branch where the waiter works.",
        summary="List Orders with Status 'Готов'",
        responses={200: OrderSerializer(many=True)}
    )
    def get(self, request, branch_id):
        if request.user.branch_id == branch_id:
            orders = Order.objects.filter(
                branch_id=branch_id, order_status='Готов').order_by('-created_at')
            serializer = OrderSerializer(orders, many=True)
            return Response(serializer.data)
        return Response({'error': 'Unauthorized or invalid branch'}, status=status.HTTP_401_UNAUTHORIZED)


@extend_schema(
    description="List all online orders",
    summary="List online Orders",
    responses={200: OrderOnlineSerializer(many=True)}
)
class OrderOnlineListView(generics.ListCreateAPIView):
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderOnlineSerializer

    # permission_classes = [IsAuthenticated]


@extend_schema(
    description="Retrieve, update, or delete an order",
    summary="Retrieve, Update, Delete Order",
    responses={200: OrderDetailedSerializer(many=False)}
)
class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderDetailedSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        branch_id = self.kwargs.get('branch_id')
        table_number = self.kwargs.get('table_number')
        order = get_object_or_404(
            Order, table__branch_id=branch_id, table__table_number=table_number)

        # Check if the order belongs to the branch where the user works
        if order.branch_id != self.request.user.branch_id:
            # If not, raise an unauthorized error
            raise PermissionDenied(
                "You don't have permission to access this order.")

        return order

    def put(self, request, *args, **kwargs):
        order_instance = self.get_object()

        # Update the order instance based on the request data
        serializer = self.get_serializer(order_instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


@extend_schema(
    description="Retrieve, update, or delete an order",
    summary="Retrieve, Update, Delete Order",
    responses={200: OrderDetailedSerializer(many=False)}
)
class OrderOnlineDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderOnlineDetailedSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        # Retrieve the order object to update
        order_instance = self.get_object()

        # Update the order instance based on the request data
        serializer = self.get_serializer(order_instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


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

    # Retrieve a table
    def get(self, request, branch_id, table_number, *args, **kwargs):
        try:
            # Retrieve the table for the given branch_id and table_number
            table = Table.objects.get(
                branch_id=branch_id, table_number=table_number)
            serializer = TableSerializer(table)
            return Response(serializer.data)
        except Table.DoesNotExist:
            return Response({'error': 'Table not found'}, status=status.HTTP_404_NOT_FOUND)

    # Create a table
    def post(self, request, branch_id, table_number, *args, **kwargs):
        # Add the branch_id and table_number to the request data
        request_data = request.data.copy()
        request_data['table_number'] = table_number
        request_data['branch'] = branch_id

        serializer = TableSerializer(data=request_data)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Table created successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Update a table
    def put(self, request, branch_id, table_number, *args, **kwargs):
        try:
            table = Table.objects.get(
                branch_id=branch_id, table_number=table_number)
        except Table.DoesNotExist:
            return Response({'error': 'Table not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = TableSerializer(table, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Table updated successfully'})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Delete a table
    def delete(self, request, branch_id, table_number, *args, **kwargs):
        try:
            table = Table.objects.get(
                branch_id=branch_id, table_number=table_number)
        except Table.DoesNotExist:
            return Response({'error': 'Table not found'}, status=status.HTTP_404_NOT_FOUND)

        table.delete()
        return Response({'message': 'Table deleted successfully'})


class TopSellingMenuItemsAPIView(APIView):
    def get(self, request, branch_id, format=None):
        # Get orders for the specific branch
        branch_orders = Order.objects.filter(
            branch_id=branch_id, order_status='Завершен')

        # Count the quantity of each menu item sold
        sold_items = branch_orders.values(
            'ITO__item_id', 'ITO__item__name').annotate(total_sold=Count('ITO__item'))

        # Sort the sold items by total_sold in descending order
        sold_items = sorted(
            sold_items, key=lambda x: x['total_sold'], reverse=True)

        # Get the top-3 best selling items
        top_selling_items = sold_items[:10]

        # Serialize the top selling items
        serialized_data = [{'name': item['ITO__item__name'],
                            'total_sold': item['total_sold']} for item in top_selling_items]

        return Response(serialized_data)


class CustomerOrdersAPIView(generics.ListAPIView):
    serializer_class = OrderOnlineDetailedSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Retrieve orders related to the authenticated customer and order them by '-created_at'
        return Order.objects.filter(customer=self.request.user).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        # Get queryset
        queryset = self.get_queryset()
        # Serialize data
        serializer = self.serializer_class(queryset, many=True)
        # Return response
        return Response(serializer.data)
