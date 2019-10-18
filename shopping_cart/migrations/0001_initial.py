# Generated by Django 2.1.5 on 2019-06-20 22:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('userprofiles2', '0001_initial'),
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ref_code', models.CharField(max_length=15)),
                ('is_ordered', models.BooleanField(default=False)),
                ('date_ordered', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_ordered', models.BooleanField(default=False)),
                ('date_added', models.DateTimeField(auto_now=True)),
                ('date_ordered', models.DateTimeField(null=True)),
                ('product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.Rent')),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(max_length=120)),
                ('order_id', models.CharField(max_length=120)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=100)),
                ('success', models.BooleanField(default=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='userprofiles2.UserProfile')),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
        migrations.AddField(
            model_name='order',
            name='items',
            field=models.ManyToManyField(to='shopping_cart.OrderItem'),
        ),
        migrations.AddField(
            model_name='order',
            name='owner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='userprofiles2.UserProfile'),
        ),
    ]