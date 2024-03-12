from django import forms
from .models import User

class UserForm(forms.ModelForm):
    class meta:
        model=User
        fields='__all__'