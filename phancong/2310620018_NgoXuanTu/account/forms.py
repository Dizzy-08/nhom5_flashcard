from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


class SignupForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ("email",)  # add email field

    def __init__(self, *args, **kwargs):  # Remove the help text
        super(SignupForm, self).__init__(*args, **kwargs)

        for fieldname in ["username", "password1", "password2"]:
            self.fields[fieldname].help_text = None

        for fieldname in ["username", "password1", "password2", "email"]:
            self.fields[fieldname].widget.attrs.update({"class": "input is-success"})


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

        for fieldname in ["username", "password"]:
            self.fields[fieldname].widget.attrs.update({"class": "input is-success"})
