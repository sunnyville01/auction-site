from django.conf import settings
from django.contrib.auth.models import User
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _
from django import forms

from cloudinary.forms import CloudinaryFileField

from . import models



class ItemCreateForm(forms.ModelForm):
    image1 = CloudinaryFileField(
                required=False,
                options = {'crop': 'limit', 'width': 546, 'height': 1000,})
    image2 = CloudinaryFileField(
                required=False,
                options = {'crop': 'limit', 'width': 546, 'height': 1000,})
    image3 = CloudinaryFileField(
                required=False,
                options = {'crop': 'limit', 'width': 546, 'height': 1000,})
    class Meta:
        model = models.Item
        fields = ("post_type", "image1", "image2", "image3", "name", "details", "category", "other_category", "location", "location_detail")
        labels = {
            'details': _('Details (optional):'),
            'category': _('Category (optional):'),
            'other_category': _('Name the Other Category (optional):'),
            'location_detail': _('Location Detail (optional):'),
        }


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')


class SignupForm(forms.Form):
    accept_tos = forms.BooleanField(required=True, label='Accept terms of use')

    def signup(self, request, user):
        user.accept_tos = self.cleaned_data['accept_tos']
        user.save()


class ChooseUserForm(forms.ModelForm):
    STATUS_CHOICES = (
        ('awaiting', 'Awaiting Pickup'),
        ('completed', 'Completed'),
    )
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
    )
    class Meta:
        model = models.Item
        fields = ('status',)


class RequestForm(forms.ModelForm):
    class Meta:
        model = models.UserMessage
        fields = ['pickup_time', 'message']
        labels = {
            'pickup_time': 'Enter a date/day/time you can pickup the item:',
            'message': 'I\'d really like the item because:',
        }


class OfferForm(forms.ModelForm):
    class Meta:
        model = models.UserMessage
        fields = ['message']
        labels = {
            'message': 'Description of item offered',
        }


class ReplyForm(forms.ModelForm):
    class Meta:
        model = models.UserMessage
        fields = ['message']
        labels = {
            'message': 'Your Reply',
        }


class AskQuestionForm(forms.ModelForm):
    class Meta:
        model = models.UserMessage
        fields = ['message']
        labels = {
            'message': 'Your Question',
        }


class ReportItemForm(forms.ModelForm):
    class Meta:
        model = models.UserMessage
        fields = ['message']
        labels = {
            'message': 'Reason for the report',
        }
