from django import forms
from .models import *
from . import models

from django.contrib.auth.models import User

# Create a UserUpdateForm to update a username and email
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["username", "email"]


# Create a ProfileUpdateForm to update image.
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["image"]


class UpdateUserForm(forms.ModelForm):
    username = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    email = forms.EmailField(
        required=True, widget=forms.TextInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = User
        fields = ["username", "email"]


class UpdateProfileForm(forms.ModelForm):
    image = forms.ImageField(
        widget=forms.FileInput(attrs={"class": "form-control-file"})
    )

    class Meta:
        model = Profile
        fields = ["image"]


class CreateNewSite(forms.ModelForm):
    site_code = forms.CharField(max_length=250, label="Company ID")
    location = forms.Textarea()
    avatar = forms.ImageField(label="Avatar")

    class Meta:
        model = models.Site
        fields = (
            "site_code",
            "location",
            "avatar",
        )

    def clean_site_code(self):
        id = self.data["id"] if self.data["id"] != "" else 0
        site_code = self.cleaned_data["site_code"]
        try:
            if id > 0:
                employee = models.Site.exclude(id=id).get(site_code=site_code)
            else:
                employee = models.Site.get(site_code=site_code)
        except:
            return site_code
        return forms.ValidationError(f"{site_code} already exists.")


###### TASK FORM #####


# Add new task
class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["task_name", "task_description", "user", "map_url", "shelter_type"]


class UpdateTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["task_name", "task_description", "status"]


class EmailForm(forms.Form):
    email = forms.EmailField(required=True)
    subject = forms.CharField(max_length=20, required=True)
    attach = forms.FileField(widget=forms.ClearableFileInput(attrs={"multiple": True}))
    message = forms.CharField(widget=forms.Textarea)
