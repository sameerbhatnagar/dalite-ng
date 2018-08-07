from __future__ import unicode_literals

from django import forms


class EmailChangeForm(forms.Form):
    """Form for user email address"""

    email = forms.EmailField()
