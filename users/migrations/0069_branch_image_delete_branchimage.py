# Generated by Django 4.2 on 2024-03-13 21:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0068_remove_branch_image_branchimage'),
    ]

    operations = [
        migrations.AddField(
            model_name='branch',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='branch_images/'),
        ),
        migrations.DeleteModel(
            name='BranchImage',
        ),
    ]