from django import forms

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from connect4.models import Profile
from django.forms.widgets import TextInput


MAX_UPLOAD_SIZE = 2500000

class LoginForm(forms.Form):
    username = forms.CharField(max_length=20, label='Username')
    password = forms.CharField(max_length=200, label='Password', widget=forms.PasswordInput())

    # Customizes form validation for properties that apply to more
    # than one field.  Overrides the forms.Form.clean function.
    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super().clean()

        # Confirms that the two password fields match
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            raise forms.ValidationError("Invalid username/password")

        # We must return the cleaned data we got from our parent.
        return cleaned_data


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=20, label='Username')
    password = forms.CharField(max_length=200,
                                label='Password',
                                widget=forms.PasswordInput())
    confirm_password = forms.CharField(max_length=200,
                                label='Confirm',
                                widget=forms.PasswordInput())
    email = forms.CharField(max_length=50, label='E-mail',
                            widget=forms.EmailInput())
    first_name = forms.CharField(max_length=20, label='First Name')
    last_name = forms.CharField(max_length=20, label='Last Name')
    primary_color = forms.CharField(label='primary_hex_color', max_length=7,
                                widget=forms.TextInput(attrs={'type': 'color'}))
    secondary_color = forms.CharField(label='secondary_hex_color', max_length=7,
                                    widget=forms.TextInput(attrs={'type': 'color'}))
    # Customizes form validation for properties that apply to more
    # than one field.  Overrides the forms.Form.clean function.
    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super().clean()

        # Confirms that the two password fields match
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            print("Passwords dont match")
            raise forms.ValidationError("Passwords did not match.")
        # We must return the cleaned data we got from our parent.
        return cleaned_data

    # Customizes form validation for the username field.
    def clean_username(self):
        # Confirms that the username is not already present in the
        # User model database.
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__exact=username):
            raise forms.ValidationError("Username is already taken.")

        # We must return the cleaned data we got from the cleaned_data
        # dictionary
        return username

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('image', 'primary_color', 'secondary_color')

        widgets = {
            'image': forms.FileInput(attrs={'id': 'id_profile_picture'}),
            'primary_color': TextInput(attrs={'type': 'color'}),
            'secondary_color': TextInput(attrs={'type': 'color'}),
        }

    def clean_image(self):
        image = self.cleaned_data['image']
        if not image or not hasattr(image, 'content_type'):
            raise forms.ValidationError('You must upload a picture')
        if not image.content_type or not image.content_type.startswith('image'):
            raise forms.ValidationError('File type is not image')
        if image.size > MAX_UPLOAD_SIZE:
            raise forms.ValidationError('File too big (max size is {0} bytes)'.format(MAX_UPLOAD_SIZE))
        return image