from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.response import Response
from .models import Category, Menu_Item, Stock, Branch, Ingredient
from .serializers import CategorySerializer, MenuItemSerializer, StockSerializer, IngredientSerializer, MenuItemListSerializer, StockAddSerializer
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.db.models import F, ExpressionWrapper, fields
from django.db.models.fields import IntegerField
from django.db.models import Case, When, Value, BooleanField
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
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
        responses={204: "No Content",
                   400: "Bad Request - Cannot delete category with associated menu items"}
    )
    def delete(self, request, *args, **kwargs):
        category = self.get_object()

        # Check if the category has associated menu items
        if category.menu_items.exists():
            return Response({"detail": "Cannot delete category with associated menu items."}, status=status.HTTP_400_BAD_REQUEST)

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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Extract ingredients data
        ingredients_data = serializer.validated_data.pop('ingredients', [])

        # Create the menu item
        menu_item = serializer.save()   # This line is causing the error

        # Create ingredients for the menu item
        for ingredient_data in ingredients_data:
            # Associate each ingredient with the menu item
            ingredient_data['menu_item'] = menu_item
            Ingredient.objects.create(**ingredient_data)

        headers = self.get_success_headers(serializer.data)
        response_serializer = MenuItemSerializer(menu_item)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class MenuItemPagination(PageNumberPagination):
    page_size = 7
    page_size_query_param = 'page_size'
    max_page_size = 100


@extend_schema(
    description="Get a list of all menu items.",
    summary="List Menu Items",
    responses={200: MenuItemListSerializer(many=True)}
)
class MenuItemList(generics.ListCreateAPIView):
    queryset = Menu_Item.objects.all()
    serializer_class = MenuItemListSerializer
    # permission_classes = [IsAuthenticated]
    pagination_class = MenuItemPagination

    @extend_schema(
        description="Get details, update, or delete a menu item.",
        summary="Retrieve/Update/Delete Menu Item",
        responses={200: MenuItemListSerializer, 204: "No Content", }
    )
    def get_queryset(self):
        queryset = Menu_Item.objects.all().order_by(F('id').desc())

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

        branch_id = self.request.query_params.get('branch_id')
        if branch_id:
            queryset = queryset.filter(branch_id=branch_id)

        return queryset

    def get(self, request, *args, **kwargs):
        response = super(MenuItemList, self).get(request, *args, **kwargs)
        pagination_data = self.get_paginated_response(response.data)
        return Response(pagination_data.data)


class MenuItemDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Menu_Item.objects.all()
    serializer_class = MenuItemListSerializer
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
    responses={201: StockAddSerializer, 204: "No Content", }
)
class StockItemCreateView(generics.CreateAPIView):
    queryset = Stock.objects.all()
    serializer_class = StockAddSerializer
    # permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Check if the stock item already exists for the given branch
        existing_stock = Stock.objects.filter(
            branch=serializer.validated_data['branch'],
            stock_item=serializer.validated_data['stock_item']
        ).first()

        if existing_stock:
            # Update the quantity and other fields
            existing_stock.current_quantity += serializer.validated_data['current_quantity']
            existing_stock.minimum_limit = serializer.validated_data.get(
                'minimum_limit', existing_stock.minimum_limit)
            existing_stock.is_enough = existing_stock.current_quantity >= existing_stock.minimum_limit
            existing_stock.save()

            headers = self.get_success_headers(serializer.data)
            response_serializer = StockAddSerializer(existing_stock)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            # Create a new stock item
            response = super().create(request, *args, **kwargs)
            return response


class StockItemsListPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 100


@extend_schema(
    description="Get a list of all stock items.",
    summary="List Stock Items",
    responses={200: StockSerializer(many=True)}
)
class StockItemsList(generics.ListCreateAPIView):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    pagination_class = StockItemsListPagination
    # permission_classes = [IsAuthenticated]

    @extend_schema(
        description="Get details, update, or delete a stock item.",
        summary="Retrieve/Update/Delete Stock Item",
        responses={200: StockSerializer, 204: "No Content", }
    )
    def get_queryset(self):
        queryset = Stock.objects.all().order_by('-restock_date')

        # Get the search parameters from the query parameters
        search_term = self.request.query_params.get('search', None)
        branch_name = self.request.query_params.get('branch_name', None)

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
        if branch_name:
            queryset = queryset.filter(branch__branch_name=branch_name)

        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

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
    pagination_class = StockItemsListPagination
    # permission_classes = [IsAuthenticated]

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

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

@extend_schema(
    description="Get a list of stock items with quantity greater than minimum for \"Готовое изделие\"",
    summary="List Stock Items with Quantity > Minimum (\"Готовое изделие\")",
    responses={200: StockSerializer(many=True)}
)
class StockItemsEnoughList(generics.ListAPIView):
    serializer_class = StockSerializer
    pagination_class = StockItemsListPagination
    # permission_classes = [IsAuthenticated]

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

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

@extend_schema(
    description="Get a list of stock items with quantity greater than minimum for \"Сырьё\"",
    summary="List Stock Items with Quantity > Minimum",
    responses={200: StockSerializer(many=True)}
)
class StockItemsRawEnoughList(generics.ListAPIView):
    serializer_class = StockSerializer
    pagination_class = StockItemsListPagination
    # permission_classes = [IsAuthenticated]

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

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

# ===========================================================================
# BRANCH MENU
# ===========================================================================

class BranchMenuView(generics.ListAPIView):
    serializer_class = MenuItemListSerializer
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        branch_id = self.kwargs.get('branch_id')

        try:
            branch = Branch.objects.get(id=branch_id)
        except Branch.DoesNotExist:
            print(f"Branch with ID {branch_id} does not exist.")
            return Menu_Item.objects.none()

        menu_items = Menu_Item.objects.all()
        print(f"Menu Items: {menu_items}")

        available_menu_items = [
            menu_item for menu_item in menu_items if self.menu_item_has_enough_ingredients(menu_item, branch)
        ]
        print(f"Available Menu Items: {available_menu_items}")

        return available_menu_items
    
    def menu_item_has_enough_ingredients(self, menu_item, branch):
        for ingredient in menu_item.ingredients.all():
            print(f"Ingredient Name: {ingredient.name}")
            try:
                stock = Stock.objects.get(
                    branch=branch, stock_item=ingredient.name)
            except Stock.DoesNotExist:
                print(f"Stock for {
                      ingredient.name} does not exist in branch {branch.id}.")
                return False

            if stock.current_quantity < ingredient.quantity:
                print(f"Not enough stock for {
                      ingredient.name} in branch {branch.id}.")
                print(f"Ingredient Quantity: {ingredient.quantity}")
                print(f"Stock Quantity: {stock.current_quantity}")
                return False

        return True


@extend_schema(
    description="Get a list of menu items in a branch filtered by category.",
    summary="Branch Menu Items by Category",
    responses={200: MenuItemListSerializer(many=True)}
)
class BranchMenuByCategoryView(generics.ListAPIView):
    serializer_class = MenuItemListSerializer
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        branch_id = self.kwargs.get('branch_id')
        category_id = self.kwargs.get('category_id')

        try:
            branch = Branch.objects.get(id=branch_id)
        except Branch.DoesNotExist:
            print(f"Branch with ID {branch_id} does not exist.")
            return Menu_Item.objects.none()

        menu_items = Menu_Item.objects.filter(
            category__id=category_id
        )

        available_menu_items = menu_items.filter(
            category__id=category_id
        )

        available_menu_items = [
            menu_item for menu_item in available_menu_items if self.menu_item_has_enough_ingredients(menu_item, branch)
        ]

        return available_menu_items

    def menu_item_has_enough_ingredients(self, menu_item, branch):
        for ingredient in menu_item.ingredients.all():
            print(f"Ingredient Name: {ingredient.name}")
            try:
                stock = Stock.objects.get(
                    branch=branch, stock_item=ingredient.name)
            except Stock.DoesNotExist:
                print(f"Stock for {
                      ingredient.name} does not exist in branch {branch.id}.")
                return False

            if stock.current_quantity < ingredient.quantity:
                print(f"Not enough stock for {
                      ingredient.name} in branch {branch.id}.")
                print(f"Ingredient Quantity: {ingredient.quantity}")
                print(f"Stock Quantity: {stock.current_quantity}")
                return False

        return True

# class ExtraItemCreateView(APIView):
#     def post(self, request, *args, **kwargs):
#         serializer = ExtraItemSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
