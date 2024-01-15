from django.forms import ModelForm, HiddenInput
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from trail.models import User, Trail
from django import forms


class NewUserForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"] 


class TrailNameForm(ModelForm):
    class Meta:
        model = Trail
        fields = ["trail_name"]
        labels = {"trail_name": "Trail name"}
        widgets = {
            "trail_name": forms.TextInput(attrs={"class":"form-control"},),
        }


class TrailDescriptionForm(ModelForm):
    class Meta:
        model = Trail
        fields = ["description"]
        labels = {"description": "Add some description"}
        widgets = {
            "description": forms.Textarea(attrs={"class":"form-control"},),
        }


class PasswordChange_Form(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.pop("autofocus", None)
        
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control mb-3'

    class Meta:
        model = User
        fields = ['__all__']