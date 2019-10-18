import datetime

from django.db.models import Count
from django.utils import timezone
from controlcenter import Dashboard, widgets
from main.models import Car, Rent, CarType

"""
class MenuWidget(widgets.ItemList):
    # This widget displays a list of pizzas ordered today
    # in the restaurant
    title = 'today orders'
    model = Car
    list_display = ['name', 'ocount']
    list_display_links = ['name']

    # By default ItemList limits queryset to 10 items, but we need all of them
    limit_to = None

    # Sets widget's max-height to 300 px and makes it scrollable
    height = 300

    def get_queryset(self):
        rent = super(MenuWidget, self).get_queryset().get()
        today = timezone.now().date()
        return (rent.car
                          .filter(orders__created__gte=today, name='ciao')
                          .order_by('-ocount')
                          .annotate(ocount=Count('orders')))
                          """
from controlcenter import app_settings
from django.utils.timesince import timesince

from django.contrib.auth.models import User
class LatestOrdersWidget(widgets.ItemList):
    # Displays latest 20 orders in the the restaurant
    title = 'Auto Plus latest rents'
    model = Rent
    queryset = (model.objects
                     .select_related('car','client')
                     .filter(created__gte=timezone.now().date(),
                             )
                     .order_by('pk'))
    # This is the magic
    list_display = [app_settings.SHARP, 'pk', 'client', 'car', 'ago']

    # If list_display_links is not defined, first column to be linked
    list_display_links = ['pk']

    # Makes list sortable
    sortable = True

    # Shows last 20
    limit_to = 20

    # Display time since instead of date.__str__
    def ago(self, obj):
        return timesince(obj.created)


#####
class CarSingleBarChart(widgets.SinglePieChart):
    # Displays score of each restaurant.
    title = 'Most popular car'
    model = Car

    """class Chartist:
        options = {
            # Displays only integer values on y-axis
            'onlyInteger': True,
            # Visual tuning
            'chartPadding': {
                'top': 24,
                'right': 0,
                'bottom': 0,
                'left': 0,
            }
        }"""

    def legend(self):
        # Duplicates series in legend, because Chartist.js
        # doesn't display values on bars
        return self.series

    def values(self):
        # Returns pairs of restaurant names and order count.
        queryset = self.get_queryset()
        return list(queryset.values_list('model')
                        .annotate(baked=Count('rent'))
                        .order_by('-baked')[:self.limit_to])

class CarSingleBarChart1(widgets.SingleBarChart):
    # Displays score of each restaurant.
    title = 'Most popular car'
    model = Car

    class Chartist:
        options = {
            # Displays only integer values on y-axis
            'onlyInteger': True,
            # Visual tuning
            'chartPadding': {
                'top': 24,
                'right': 0,
                'bottom': 0,
                'left': 0,
            }
        }

    def legend(self):
        # Duplicates series in legend, because Chartist.js
        # doesn't display values on bars
        return self.series

    def values(self):
        # Returns pairs of restaurant names and order count.
        queryset = self.get_queryset()
        return list(queryset.values_list('model')
                        .annotate(baked=Count('rent'))
                        .order_by('-baked')[:self.limit_to])

from collections import defaultdict

class OrderLineChart(widgets.LineChart):
    # Displays orders dynamic for last 7 days
    title = 'Orders this week'
    model = Rent
    limit_to = 7
    # Lets make it bigger
    width = widgets.LARGER

    class Chartist:
        # Visual tuning
        options = {
            'axisX': {
                'labelOffset': {
                    'x': -24,
                    'y': 0
                },
            },
            'chartPadding': {
                'top': 24,
                'right': 24,
            }
        }

    def legend(self):
        # Displays restaurant names in legend
        CARS= Car.objects.all()
        return CARS

    def labels(self):
        # Days on x-axis
        today = timezone.now().date()
        labels = [(today - datetime.timedelta(days=x)).strftime('%d.%m')
                  for x in range(self.limit_to)]
        return labels

    def series(self):
        # Some dates might not exist in database (no orders are made that
        # day), makes sure the chart will get valid values.
        series = []
        for Rent.car in self.legend:
            # Sets zero if date not found
            item = self.values.get(Rent.car, {})
            series.append([item.get(label, 0) for label in self.labels
            ])
        return series

    def values(self):
        # Increases limit_to by multiplying it on restaurant quantity
        limit_to = self.limit_to * len(self.legend)
        queryset = self.get_queryset()
        # This is how `GROUP BY` can be made in django by two fields:
        # restaurant name and date.
        # Ordered.created is datetime type but we need to group by days,
        # here we use `DATE` function (sqlite3) to convert values to
        # date type.
        # We have to sort by the same field or it won't work
        # with django ORM.
        queryset = (queryset.extra({'baked':
                                    'DATE(created)'})
                            .select_related('car_type__name')
                            .values_list('car__model', 'baked')
                            .order_by('-baked')
                            .annotate(ocount=Count('pk'))[:limit_to])

        # The key is restaurant name and the value is a dictionary of
        # date:order_count pair.
        values = defaultdict(dict)
        for Rent.car, date, count in queryset:
            # `DATE` returns `YYYY-MM-DD` string.
            # But we want `DD-MM`
            day_month = '{2}.{1}'.format(*date.split('-'))
            values[Rent.car][day_month] = count
        return values

class MyBarChart(widgets.SingleBarChart):
        # label and series
        values_list = ('car_type__name', 'rating')
        # Data source
        queryset = Car.objects.order_by('-rating')
        limit_to = 8

class MyDashboard(Dashboard):
    widgets = (
        LatestOrdersWidget, widgets.Group([CarSingleBarChart, CarSingleBarChart1]), MyBarChart, OrderLineChart,
    )