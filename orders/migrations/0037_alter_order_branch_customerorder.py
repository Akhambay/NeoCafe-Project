# Generated by Django 4.2 on 2024-03-29 04:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0077_alter_customuser_user_type'),
        ('orders', '0036_alter_order_customer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='branch',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='orders', related_query_name='order', to='users.branch'),
        ),
        migrations.CreateModel(
            name='CustomerOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_status', models.CharField(default='Новый', max_length=20)),
                ('order_type', models.CharField(default='Takeaway', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('total_price', models.PositiveIntegerField(default=0)),
                ('order_number', models.PositiveIntegerField(blank=True, null=True)),
                ('branch', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='customer_orders', to='users.branch')),
                ('customer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='customers_orders', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
