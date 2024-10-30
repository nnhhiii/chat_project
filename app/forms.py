from django import forms
from .models import ChatRoom

class LoginForm(forms.Form):
    email = forms.CharField(max_length=50)
    password = forms.CharField(widget=forms.PasswordInput)


class GroupForm(forms.ModelForm):
    class Meta:
        model = ChatRoom
        fields = ['name']