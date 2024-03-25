from orders.models import Order

# Assuming 'id' is the primary key
order = Order.objects.get(id=83)
order.customer_id = 78
order.save()
