from django.forms import ModelForm, ValidationError, DateInput, DateField, Form, ChoiceField, Select
#from django.forms.extras.widgets import SelectDateWidget
from main.models import *
from django import forms

from datetime import datetime

from main.models import Rent


class RentForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(RentForm, self).__init__(*args, **kwargs)
        self.fields['start_date'].widget = DateInput(attrs={'class':'form-control date-selector'
        ,'placeholder':'enter start date','autocomplete':'off'},format=('%d-%m-%Y'))
        self.fields['end_date'].widget = DateInput(attrs={'class':'form-control date-selector'
        ,'placeholder':'enter end date','autocomplete':'off'},format=('%d-%m-%Y'))
        #start_date = DateField(label='Start date', input_formats=['%Y-%m-%d'], attrs={'class':'form-control'})
        #end_date = DateField(label='End date', input_formats=['%Y-%m-%d'], attrs={'class':'form-control'})

    def clean(self):
        data = super(RentForm, self).clean()
        start = data.get('start_date')
        end = data.get('end_date')
        if start and end:
            now = datetime.now().date()
            diff = (now - start).total_seconds()
            if diff > 0:
                raise ValidationError("Both dates have to be in the future.")

            days = (end - start).days
            if days < 1:
                raise ValidationError("The rent period has to be at least one full day.")

    class Meta:
        model = Rent
        fields = ['start_date', 'end_date']


class CarFilterForm(Form):
    CAR_TYPES = [(i.id, i.name) for i in CarType.objects.all()]
    CAR_TYPES.insert(0, ("", "All"))

    ACCESSORIES = [(i.id, i.name) for i in CarAccessory.objects.all()]

    ENGINE_TYPES = [(i.id, i.name) for i in EngineType.objects.all()]
    ENGINE_TYPES.insert(0, ("", "All"))

    car_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'autocomplete':'off','placeholder':'Car name'}))
    car_type = ChoiceField(required=False, widget=Select, choices=CAR_TYPES)
    engine_type = ChoiceField(required=False, widget=Select, choices=ENGINE_TYPES)
    accessories = forms.MultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple, choices=ACCESSORIES)
    price_from = forms.CharField(required=False, widget=forms.NumberInput(attrs={'autocomplete':'off','placeholder':'min amount'}))
    price_to = forms.CharField(required=False, widget=forms.NumberInput(attrs={'autocomplete':'off','placeholder':'max amount'}))
    start_date = forms.DateField(required=False, widget=DateInput(attrs={'class': 'date-selector','autocomplete':'off','placeholder':'enter start date'}))
    end_date = forms.DateField(required=False, widget=DateInput(attrs={'class': 'date-selector','autocomplete':'off','placeholder':'enter end date'}))
    min_rating = forms.CharField(required=False, widget=forms.NumberInput(attrs={'type': 'number', 'min': '0', 'max': '10', 'step': '1'}))


class CommentForm(ModelForm):
		car_id = forms.CharField(widget=forms.HiddenInput)
		content = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))

		def __init__(self, *args, **kwargs):
				super(CommentForm, self).__init__(*args, **kwargs)

		def clean(self):
				data = super(CommentForm, self).clean()

		class Meta:
				model = Comment
				fields = ['content']

class ContactForm(forms.Form):
    name = forms.CharField(required=True, max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}) )
    email = forms.EmailField(required=True, max_length=100, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    message = forms.CharField(widget=forms.Textarea)
