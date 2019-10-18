from django.conf.urls import url

from main.views import CarListView, CarDetailView, RentCreateView, MyRentedCarListView, RentDeleteView, AddCommentView, carRate, contact_us

urlpatterns = [
    url(r'^$', CarListView.as_view(), {'page': 1}, name='index'),
    # example: car/list
    url(r'^car/list/$', CarListView.as_view(), {'page': 1}, name='car_list_default'),
    # example: car/list/2
    url(r'^car/list/(?P<page>[0-9]+)/$', CarListView.as_view(), name='car_list'),
    # example: car/12
    url(r'^car/(?P<car_id>[0-9]+)/$', CarDetailView.as_view(), name='car_detail'),
	# example: car/12/add_comment
    url(r'^car/(?P<car_id>[0-9]+)/add_comment$', AddCommentView.as_view(), name='add_comment'),
    # example: rent/1
    url(r'^rent/(?P<car_id>[0-9]+)/$', RentCreateView.as_view(), name='rent_create'),
    #
    url(r'^rent/cancel/(?P<rent_id>[0-9]+)/$', RentDeleteView.as_view(), name='rent_delete'),
    #
    url(r'^history/list/$', MyRentedCarListView.as_view(), {'page': 1}, name='my_history_list_default'),
    #
    url(r'^history/list/(?P<page>[0-9]+)/$', MyRentedCarListView.as_view(), name='my_history_list'),
    #
    url(r'^carRate/$', carRate, name='game_rate'),
    #
    url(r'^contact-us/$', contact_us, name='contact_us'),

]
