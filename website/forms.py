from django import forms
from .models import Company, Trip

class QuoteRequestForm(forms.Form):
    FREIGHT_CHOICES = [
        ('1 Ton', 'One Ton Pickup Freight'),
        ('3 Ton', 'Three Ton Pickup Freight'),
        ('7 Ton', 'Seven Ton Pickup Freight'),
        ('10 Ton', 'Ten Ton Pickup Freight'),
        ('truck', 'Truck Freight'),
    ]
    
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    mobile = forms.CharField(max_length=15)
    freight = forms.ChoiceField(choices=FREIGHT_CHOICES)
    origin = forms.CharField(max_length=100)
    destination = forms.CharField(max_length=100)
    note = forms.CharField(widget=forms.Textarea, required=False)


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'email', 'phone', 'contact_person', 'address','po_box']



class TripForm(forms.ModelForm):
    company = forms.ModelChoiceField(queryset=Company.objects.all(), empty_label="Select Company")

    class Meta:
        model = Trip
        fields = ['company', 'date', 'freight', 'origin', 'destination', 'amount', 'driver','toll_gate']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

class LoginRequestForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(max_length=25)