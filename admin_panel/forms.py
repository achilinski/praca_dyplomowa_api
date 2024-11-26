from django import forms

class UserStatsFilterForm(forms.Form):
    username = forms.CharField(required=False, label="Username", widget=forms.TextInput(attrs={'placeholder': 'Enter username'}))
    start_date = forms.DateField(required=False, label="Start Date", widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(required=False, label="End Date", widget=forms.DateInput(attrs={'type': 'date'}))
