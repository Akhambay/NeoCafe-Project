from django.urls import path
from .views import (OrderView, OrderOnlineView, WaiterOrdersView, OrderOnlineListView, OrderDetailView,
                    TableView, TableCreateView, TableListView, TableDetailedView, OrderOnlineDetailView,
                    TopSellingMenuItemsAPIView, OrderDetailByIdView, OrderOnlineDetailByIdView,
                    ReadyOrdersListView, InProgressOrdersListView, NewOrdersView,
                    CustomerOrdersAPIView, CustomerPastOrdersAPIView, CustomerOngoingOrdersAPIView,
                    AllOrdersInBranchAPIView, OrdersOnlineNewInBranchAPIView, OrdersOnlineInProgressInBranchAPIView,
                    OrdersOnlineCancelledInBranchAPIView,OrdersOnlineDoneInBranchAPIView)

urlpatterns = [

    path('orders/add/', OrderView.as_view(), name='order-create'),
    path('orders-online/add/', OrderOnlineView.as_view(),
         name='order-online-create'),

    path('orders/all/<int:branch_id>/',
         WaiterOrdersView.as_view(), name='order-list'),
    path('orders-online/all/', AllOrdersInBranchAPIView.as_view(),
         name='order-online-list'),

     path('orders-online-list/new/', OrdersOnlineNewInBranchAPIView.as_view(),
         name='order-online-list'),

     path('orders-online-list/inprogress/', OrdersOnlineInProgressInBranchAPIView.as_view(),
         name='order-online-list'),

     path('orders-online-list/cancelled/', OrdersOnlineCancelledInBranchAPIView.as_view(),
         name='order-online-list'),

     path('orders-online-list/done/', OrdersOnlineDoneInBranchAPIView.as_view(),
         name='order-online-list'),

    path('orders/<int:order_id>/',
         OrderDetailByIdView.as_view(), name='order-create'),

    path('orders-online/<int:order_id>/',
         OrderOnlineDetailByIdView.as_view(), name='order-create'),

    path('orders/new/<int:branch_id>/',
         NewOrdersView.as_view(), name='waiter_new_orders'),
    path('orders/ready/<int:branch_id>/',
         ReadyOrdersListView.as_view(), name='waiter_ready_orders'),
    path('orders/inprogress/<int:branch_id>/',
         InProgressOrdersListView.as_view(), name='waiter_inprogress_orders'),

    path('orders/<int:branch_id>/detail/<int:table_number>/',
         OrderDetailView.as_view(), name='order-detail'),

    path('tables/create/', TableCreateView.as_view(), name='table-create'),
    path('tables/branch/<int:branch_id>/',
         TableListView.as_view(), name='table-list'),
    path('tables/', TableView.as_view()),
    path('tables/branch/<int:branch_id>/<int:table_number>/',
         OrderDetailView.as_view()),
    path('tables/branch/<int:branch_id>/edit-table/<int:table_number>/',
         TableDetailedView.as_view()),


    path('orders/online/<int:order_id>/',
         OrderOnlineDetailView.as_view()),

    path('branch/<int:branch_id>/top-selling-menu-items/',
         TopSellingMenuItemsAPIView.as_view(), name='top_selling_menu_items'),

    path('customer/orders/', CustomerOrdersAPIView.as_view(), name='customer_orders'),
    path('customer/orders/now/', CustomerOngoingOrdersAPIView.as_view(), name='customer_orders_now'),
    path('customer/orders/past/', CustomerPastOrdersAPIView.as_view(), name='customer_orders_past'),
]