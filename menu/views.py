from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.response import Response
from .models import Category, Menu_Item, Stock
from .serializers import CategorySerializer, MenuItemSerializer, StockSerializer
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.db.models import F, ExpressionWrapper, fields
from django.db.models.fields import IntegerField
from django.db.models import Case, When, Value, BooleanField

# ===========================================================================
# CATEGORY
# ===========================================================================


@extend_schema(
    description="Create a new category.",
    summary="Create Category",
    responses={201: CategorySerializer, 204: "No Content", }
)
class CategoryCreateView(generics.CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    # permission_classes = [IsAuthenticated]


@extend_schema(
    description="Get a list of all categories.",
    summary="List Categories",
    responses={200: CategorySerializer(many=True)}
)
class CategoryList(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    # permission_classes = [IsAuthenticated]


@extend_schema(
    description="Get details, update, or delete a category.",
    summary="Retrieve/Update/Delete Category",
    responses={200: CategorySerializer, 204: "No Content", }
)
class CategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    # permission_classes = [IsAuthenticated]

    @extend_schema(
        description="Get details, update, or delete a category.",
        summary="Retrieve/Update/Delete category",
        responses={
            200: CategorySerializer,
            204: "No Content",
        }
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @extend_schema(
        description="Update a category.",
        summary="Update category",
        responses={200: CategorySerializer, 204: "No Content", }
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @extend_schema(
        description="Delete a category.",
        summary="Delete category",
        responses={204: "No Content", }
    )
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

# ===========================================================================
# MENU ITEM
# ===========================================================================


@extend_schema(
    description="Create a new menu item.",
    summary="Create Menu Item",
    responses={201: MenuItemSerializer, 204: "No Content", }
)
class MenuItemCreateView(generics.CreateAPIView):
    queryset = Menu_Item.objects.all()
    serializer_class = MenuItemSerializer
    # permission_classes = [IsAuthenticated]


@extend_schema(
    description="Get a list of all menu items.",
    summary="List Menu Items",
    responses={200: MenuItemSerializer(many=True)}
)
class MenuItemList(generics.ListCreateAPIView):
    queryset = Menu_Item.objects.all()
    serializer_class = MenuItemSerializer
    # permission_classes = [IsAuthenticated]

    @extend_schema(
        description="Get details, update, or delete a menu item.",
        summary="Retrieve/Update/Delete Menu Item",
        responses={200: MenuItemSerializer, 204: "No Content", }
    )
    def get_queryset(self):
        queryset = Menu_Item.objects.all()

        # Get the search parameters from the query parameters
        search_term = self.request.query_params.get('search', None)

        if search_term:
            try:
                # Try to convert the search term to a numeric value
                search_term_numeric = float(search_term)

                # Use Q objects to filter by name, category, and price
                queryset = queryset.filter(
                    Q(name__icontains=search_term) |
                    Q(category__name__icontains=search_term) |
                    Q(price_per_unit=search_term_numeric)
                )
            except ValueError:
                # Handle the case where the search term is not a valid numeric value
                queryset = queryset.filter(
                    Q(name__icontains=search_term) |
                    Q(category__name__icontains=search_term)
                )

        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class MenuItemDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Menu_Item.objects.all()
    serializer_class = MenuItemSerializer
   # permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        existing_item_image = serializer.instance.item_image
        serializer.save()

        if 'item_image' not in self.request.data or not self.request.data['item_image']:
            serializer.instance.item_image = existing_item_image
            serializer.instance.save()


# ===========================================================================
# STOCK ITEMS
# ===========================================================================
@extend_schema(
    description="Create a new stock item.",
    summary="Create Stock Item",
    responses={201: StockSerializer, 204: "No Content", }
)
class StockItemCreateView(generics.CreateAPIView):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    # permission_classes = [IsAuthenticated]


@extend_schema(
    description="Get a list of all stock items.",
    summary="List Stock Items",
    responses={200: StockSerializer(many=True)}
)
class StockItemsList(generics.ListCreateAPIView):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    # permission_classes = [IsAuthenticated]

    @extend_schema(
        description="Get details, update, or delete a stock item.",
        summary="Retrieve/Update/Delete Stock Item",
        responses={200: StockSerializer, 204: "No Content", }
    )
    def get_queryset(self):
        queryset = Stock.objects.all()

        # Get the search parameters from the query parameters
        search_term = self.request.query_params.get('search', None)

        if search_term:
            try:
                # Try to convert the search term to a numeric value
                search_term_numeric = float(search_term)

                # Use Q objects to filter by name, category, and price
                queryset = queryset.filter(
                    Q(stock_item__icontains=search_term)
                )
            except ValueError:
                # Handle the case where the search term is not a valid numeric value
                queryset = queryset.filter(
                    Q(stock_item__icontains=search_term)
                )

        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class StockItemDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    # permission_classes = [IsAuthenticated]


@extend_schema(
    description="Get a list of stock items of minimum or less quantity.",
    summary="List Stock Items with Quantity <= Minumum",
    responses={200: StockSerializer(many=True)}
)
class StockItemsNotEnoughList(generics.ListAPIView):
    serializer_class = StockSerializer

    def get_queryset(self):
        queryset = Stock.objects.annotate(
            status_false=Case(
                When(current_quantity__lte=F('minimum_limit'), then=True),
                default=False,
                output_field=BooleanField()
            )
        ).filter(status_false=True)

        # Get the search parameters from the query parameters
        search_term = self.request.query_params.get('search', None)

        if search_term:
            try:
                # Try to convert the search term to a numeric value
                search_term_numeric = float(search_term)

                # Use Q objects to filter by stock_item and other fields as needed
                queryset = queryset.filter(
                    Q(stock_item__icontains=search_term) |
                    # Add other fields as needed
                    Q(other_field__icontains=search_term)
                )
            except ValueError:
                # Handle the case where the search term is not a valid numeric value
                queryset = queryset.filter(
                    Q(stock_item__icontains=search_term)
                )

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


@extend_schema(
    description="Get a list of stock items with quantity greater than minimum for \"Готовое изделие\"",
    summary="List Stock Items with Quantity > Minimum (\"Готовое изделие\")",
    responses={200: StockSerializer(many=True)}
)
class StockItemsEnoughList(generics.ListAPIView):
    serializer_class = StockSerializer

    def get_queryset(self):
        queryset = Stock.objects.filter(
            # Assuming 'Готовое' is the first choice
            type=Stock.TYPE_CHOICES[0][0],
            current_quantity__gt=F('minimum_limit')
        )

        # Get the search parameters from the query parameters
        search_term = self.request.query_params.get('search', None)

        if search_term:
            try:
                # Try to convert the search term to a numeric value
                search_term_numeric = float(search_term)

                # Use Q objects to filter by stock_item and other fields as needed
                queryset = queryset.filter(
                    Q(stock_item__icontains=search_term)
                )
            except ValueError:
                # Handle the case where the search term is not a valid numeric value
                queryset = queryset.filter(
                    Q(stock_item__icontains=search_term)
                )

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


@extend_schema(
    description="Get a list of stock items with quantity greater than minimum for \"Сырьё\"",
    summary="List Stock Items with Quantity > Minimum",
    responses={200: StockSerializer(many=True)}
)
class StockItemsRawEnoughList(generics.ListAPIView):
    serializer_class = StockSerializer

    def get_queryset(self):
        queryset = Stock.objects.filter(
            # Assuming 'Из сырья' is the second choice
            type=Stock.TYPE_CHOICES[1][0],
            current_quantity__gt=F('minimum_limit')
        )

        # Get the search parameters from the query parameters
        search_term = self.request.query_params.get('search', None)

        if search_term:
            try:
                # Try to convert the search term to a numeric value
                search_term_numeric = float(search_term)

                # Use Q objects to filter by stock_item and other fields as needed
                queryset = queryset.filter(
                    Q(stock_item__icontains=search_term)
                )
            except ValueError:
                # Handle the case where the search term is not a valid numeric value
                queryset = queryset.filter(
                    Q(stock_item__icontains=search_term)
                )

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
