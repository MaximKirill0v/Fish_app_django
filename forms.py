from .models import Catch
from django import forms


class AddCatchForm(forms.ModelForm):
    class Meta:
        model = Catch
        fields = ['date', 'time', 'type_of_fish', 'description', 'bait', 'fish_weight']
