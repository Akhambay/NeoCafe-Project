# Generated by Django 4.2.11 on 2024-04-19 10:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0036_alter_extraitem_options_and_more'),
        ('orders', '0045_alter_order_order_type'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ExtraItemToOrder',
            new_name='OrderItemExtraProduct',
        ),
        migrations.RenameField(
            model_name='orderitemextraproduct',
            old_name='extra_item',
            new_name='extra_product',
        ),
        migrations.AlterUniqueTogether(
            name='orderitemextraproduct',
            unique_together=set(),
        ),
    ]
