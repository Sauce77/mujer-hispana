# forms.py
from django import forms

class DateFilterForm(forms.Form):
    start_date = forms.DateField(
        label='Fecha de Inicio',
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False # Puedes hacerlo requerido o no, según tu lógica
    )
    end_date = forms.DateField(
        label='Fecha de Fin',
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )