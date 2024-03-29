# Generated by Django 4.2 on 2024-02-17 10:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0026_alter_customuser_user_type'),
        ('menu', '0009_remove_stock_branch_branchstock_stock_stock_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stock',
            name='stock',
        ),
        migrations.AddField(
            model_name='stock',
            name='branch',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='stocks', to='users.branch'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='menu_item',
            name='branch',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='menu_items_branch', to='users.branch'),
        ),
        migrations.AlterField(
            model_name='menu_item',
            name='name',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='menu_items_name', to='users.branch'),
        ),
        migrations.DeleteModel(
            name='BranchStock',
        ),
    ]
