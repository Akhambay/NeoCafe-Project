from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.response import Response
from .models import Category, Menu_Item
from .serializers import CategorySerializer, MenuItemSerializer
from rest_framework.permissions import IsAuthenticated
# CATEGORY


@extend_schema(
    description="Create a new category.",
    summary="Create Category",
    responses={201: CategorySerializer, 204: "No Content", }
)
class CategoryCreateView(generics.CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]


@extend_schema(
    description="Get a list of all categories.",
    summary="List Categories",
    responses={200: CategorySerializer(many=True)}
)
class CategoryList(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]


@extend_schema(
    description="Get details, update, or delete a category.",
    summary="Retrieve/Update/Delete Category",
    responses={200: CategorySerializer, 204: "No Content", }
)
class CategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        existing_category_image = serializer.instance.category_image
        serializer.save()

        if 'category_image' not in self.request.data or not self.request.data['category_image']:
            serializer.instance.category_image = existing_category_image
            serializer.instance.save()

# MENU_ITEM


@extend_schema(
    description="Create a new menu item.",
    summary="Create Menu Item",
    responses={201: MenuItemSerializer, 204: "No Content", }
)
class MenuItemCreateView(generics.CreateAPIView):
    queryset = Menu_Item.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticated]


@extend_schema(
    description="Get a list of all menu items.",
    summary="List Menu Items",
    responses={200: MenuItemSerializer(many=True)}
)
class MenuItemList(generics.ListCreateAPIView):
    queryset = Menu_Item.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticated]


@extend_schema(
    description="Get details, update, or delete a menu item.",
    summary="Retrieve/Update/Delete Menu Item",
    responses={200: MenuItemSerializer, 204: "No Content", }
)
class MenuItemDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Menu_Item.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        existing_item_image = serializer.instance.item_image
        serializer.save()

        if 'item_image' not in self.request.data or not self.request.data['item_image']:
            serializer.instance.item_image = existing_item_image
            serializer.instance.save()
