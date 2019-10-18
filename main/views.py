from django.views.generic import ListView, DetailView, CreateView, DeleteView, View
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.forms.utils import ErrorList
from django.shortcuts import Http404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.db.models import Avg, Count
from main.models import Car, Rent, User
from main.forms import *
from datetime import datetime
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings


class CarListView(ListView):
    model = Car
    template_name = 'main/car_list.html'
    context_object_name = 'car_list'
    paginate_by = 8

    def get_context_data(self, **kwargs):
        context = super(CarListView, self).get_context_data(**kwargs)
        context['filter'] = CarFilterForm(self.request.GET)

        return context

    def get_queryset(self):
        qs = Car.objects.all()
        rents = Rent.objects.all()

        form = CarFilterForm(self.request.GET)
        if form.is_valid():
            car_name = form.cleaned_data['car_name']
            car_type = form.cleaned_data['car_type']
            engine_type = form.cleaned_data['engine_type']
            accessories = form.cleaned_data['accessories']
            price_from = form.cleaned_data['price_from']
            price_to = form.cleaned_data['price_to']
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            min_rating = form.cleaned_data['min_rating']

            if start_date:
                qs = qs.exclude(Q(rent__start_date__lte=start_date) & Q(rent__end_date__gte=start_date))
            if end_date:
                qs = qs.exclude(Q(rent__start_date__lte=end_date) & Q(rent__end_date__gte=end_date))
            if start_date and end_date:
                qs = qs.exclude(Q(rent__start_date__gte=start_date) & Q(rent__end_date__lte=end_date))
            if car_name:
                qs = qs.filter(Q(producer__contains=car_name) |Q(model__contains=car_name))
            if car_type:
                qs = qs.filter(car_type=car_type)
            if engine_type:
                qs = qs.filter(engine_type=engine_type)
            if price_from:
                qs = qs.filter(rent_cost__gte=price_from)
            if price_to:
                qs = qs.filter(rent_cost__lte=price_to)
            if min_rating:
                qs = qs.annotate(avg_rating=Avg('rating__rating')).filter(avg_rating__gt=min_rating)

            for accessory in accessories:
                qs = qs.filter(car_accessories__id=accessory)

        return qs

class MyRentedCarListView(ListView):
    model = Rent
    template_name = 'main/my_rented_car_list.html'
    context_object_name = 'my_rented_car_list'
    paginate_by = 6

    def get_context_data(self, **kwargs):
        context = super(MyRentedCarListView, self).get_context_data(**kwargs)

        category = self.kwargs.get('category')
        if category:
            context['current_category'] = category
        return context

    def get_queryset(self):
        rents = Rent.objects.all().filter(client=self.request.user.id).order_by("-start_date", "-end_date")

        return rents

class CarDetailView(DetailView):
    model = Car
    template_name = 'main/car_detail.html'
    context_object_name = 'car'
    pk_url_kwarg = 'car_id'
    form_class = CommentForm

    def get_context_data(self, **kwargs):
        context = super(CarDetailView, self).get_context_data(**kwargs)
        context['accessories'] = context['car'].car_accessories.all()
        context['form'] = CommentForm(initial={'car_id': context['car'].id})
        context['rating'] = Rating.objects.all().filter(car= context['car'].id).aggregate(Avg('rating'))
        return context

class AddCommentView(View):
    model = Comment
    form_class = CommentForm
    template_name = 'main/car_detail.html'
    context_object_name = 'form'
    pk_url_kwarg = 'car_id'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(AddCommentView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        self.request = request
        if form.is_valid():
            self.form_valid(form)
            return HttpResponseRedirect('/car/' + form.cleaned_data['car_id'] + '/')
        return HttpResponseRedirect('/car/' + form.cleaned_data['car_id'] + '/')

    def get_context_data(self, **kwargs):
        context = super(AddCommentView, self).get_context_data(**kwargs)
        context['form'] = CommentForm(self.request.POST)
        context['car'] = self.car
        return context

    def form_valid(self, form):
        form.instance.content = form.cleaned_data['content']
        if self.request.user.is_authenticated:
            form.instance.user = get_object_or_404(User, username=self.request.user.username)
        else:
            form.instance.user = None
        form.instance.date = datetime.now()
        form.instance.car = get_object_or_404(Car, id=form.cleaned_data['car_id'])
        rents = Rent.objects.filter(car=form.instance.car).filter(Q(end_date__lte=form.instance.date)).filter(Q(client=form.instance.user)).count()
        if rents > 0:
            form.instance.comment_status = True
        else:
            form.instance.comment_status = False
        form.save()
        return True


class RentCreateView(SuccessMessageMixin, CreateView):
    model = Rent
    form_class = RentForm
    success_url = '/'
    success_message = "Car was created successfully purchased."

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(RentCreateView, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        self.car = get_object_or_404(Car, pk=self.kwargs['car_id'])
        return super(RentCreateView, self).get_form_kwargs()

    def get_context_data(self, **kwargs):
        context = super(RentCreateView, self).get_context_data(**kwargs)
        context['car'] = self.car
        return context

    def form_valid(self, form):
        start = form.cleaned_data['start_date']
        end = form.cleaned_data['end_date']

        # check if this car is available in requested period
        rents = Rent.objects.filter(car=self.car).filter(Q(start_date__lte=end) & Q(end_date__gte=start)).count()
        if rents > 0:
            errors = form._errors.setdefault("start_date", ErrorList())
            errors.append("This car is unavailable during this time. Please, select another dates.")
            return self.form_invalid(form)

        # populate Rent fields
        form.instance.client = self.request.user
        form.instance.rent_cost = self.car.rent_cost * (end - start).days
        form.instance.car_id = self.car.pk
        form.save()
        return super(RentCreateView, self).form_valid(form)


class RentDeleteView(DeleteView):
    model = Rent
    template_name = 'main/rent_cancel.html'
    pk_url_kwarg = 'rent_id'
    context_object_name = 'rent'
    success_url = '/history/list/'

def carRate(request):
    if request.method == 'POST':
        rate = request.POST['rate']
        car = request.POST['car']
        car = Car.objects.get(id=car)
        user = request.user
        try:
            rating = Rating.objects.get(car = car, user = user)
            rating.rating = rate
        except Rating.DoesNotExist:
            rating = Rating(car = car, user = user, rating = rate, date=datetime.now())
        rating.save();

        return HttpResponseRedirect('/history/list/')
    else:
        return HttpResponseRedirect('/')

def contact_us(request):
        
        form = ContactForm(request.POST or None)
        if form.is_valid():
            #hhhhhhh
            form_email = form.cleaned_data.get('email')
            form_message = form.cleaned_data.get('message')
            form_name = form.cleaned_data.get('name')

            subject = "mail"
            from_email = settings.EMAIL_HOST_USER
            to_email = [from_email, "auto@gmail.com"]
            contact_message = '%s: %s via %s'%(
                form_name,
                form_message,
                form_email)
            send_mail(subject, contact_message, form_email, to_email, fail_silently=False)
            messages.success (request, "Thank you! Your message was successfully delevered!")
        return render(request, 'main/contact-us.html', {'form': form})