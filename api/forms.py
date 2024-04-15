from django import forms


class MessageForm(forms.Form):
    row_one = forms.CharField(max_length=16, blank=True)
    row_two = forms.CharField(max_length=16, blank=True)
