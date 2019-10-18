from django.db import models
from django.contrib.auth.models import User
from datetime import date, timedelta


class Client(models.Model):
	user = models.OneToOneField(User,on_delete=models.DO_NOTHING,)
	phone_number = models.CharField(max_length=12, unique=True)
	pesel = models.CharField(max_length=12, unique=True)

	def __str__(self):
		return self.first_name + " " + self.last_name


class CarType(models.Model):
	name = models.CharField(max_length=30, unique=True)

	def __str__(self):
		return self.name


class EngineType(models.Model):
	name = models.CharField(max_length=30, unique=True)

	def __str__(self):
		return self.name


class CarAccessory(models.Model):
	name = models.CharField(max_length=30, unique=True)

	def __str__(self):
		return self.name


class Car(models.Model):
	car_image = models.ImageField()
	car_image1 = models.ImageField(blank=True)
	car_image2 = models.ImageField(blank=True)
	car_image3 = models.ImageField(blank=True)
	car_image4 = models.ImageField(blank=True)
	car_image5 = models.ImageField(blank=True)
	car_type = models.ForeignKey(CarType,on_delete=models.DO_NOTHING,)
	engine_type = models.ForeignKey(EngineType,on_delete=models.DO_NOTHING,)
	car_accessories = models.ManyToManyField(CarAccessory)
	producer = models.CharField(max_length=30)
	model = models.CharField(max_length=30)
	engine_capacity = models.DecimalField(max_digits=6, decimal_places=2)
	engine_horsepower = models.DecimalField(max_digits=6, decimal_places=2)
	seats_quantity = models.IntegerField()
	doors_quantity = models.IntegerField()
	load_capacity = models.IntegerField()
	production_year = models.IntegerField()
	vin_number = models.CharField(max_length=17, unique=True)
	rent_cost = models.DecimalField(max_digits=8, decimal_places=3)

	comments = models.ManyToManyField(User, through='Comment', through_fields=('car', 'user'), related_name='users_that_commented')
	ratings = models.ManyToManyField(User, through='Rating', through_fields=('car', 'user'), related_name='users_that_rated')

	def __str__(self):
		return self.car_type.name + " (" + self.vin_number + ")"


class Rent(models.Model):
	client = models.ForeignKey(User,on_delete=models.DO_NOTHING,)
	car = models.ForeignKey(Car,on_delete=models.DO_NOTHING,)
	rent_cost = models.DecimalField(max_digits=8, decimal_places=2)
	start_date = models.DateField()
	end_date = models.DateField()
	created = models.DateTimeField(auto_now_add=True)

	@property
	def is_start_past_or_today(self):
		if date.today() >= self.start_date:
			return True
		return False

	@property
	def is_end_future_or_today(self):
		if date.today() <= self.end_date:
			return True
		return False

	@property
	def can_be_cancelled(self):
		if date.today() + timedelta(days=3) <= self.start_date:
			return True
		return False

	def __str__(self):
		client_and_car_info = self.client.__str__() + ", " + self.car.__str__()
		date_range_info = "from " + self.start_date.__str__() + " to " + self.end_date.__str__()
		cost_info = "(" + self.rent_cost.__str__() + ")"
		return client_and_car_info + " " + date_range_info + " " + cost_info

class Comment(models.Model):
	user = models.ForeignKey(User,on_delete=models.DO_NOTHING,)
	car = models.ForeignKey(Car,on_delete=models.DO_NOTHING,)
	content = models.CharField(max_length = 1000)
	date = models.DateTimeField()
	comment_status = models.BooleanField(default = False)

	class Meta:
		ordering = ['-date',]

	def __str__(self):
		return self.content

class Rating(models.Model):
	user = models.ForeignKey(User,on_delete=models.DO_NOTHING,)
	car = models.ForeignKey(Car,on_delete=models.DO_NOTHING,)
	rating = models.IntegerField()
	date = models.DateTimeField()

	class Meta:
		unique_together = ('user', 'car')

	def clean(self):
		if(self.rating < 1 or self.rating > 10):
			raise ValidationError('Rating needs to be in a range of 1 to 10!')
