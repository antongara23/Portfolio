from django import forms
from .models import Message, Ad


class NewMessage(forms.ModelForm):
    class Meta:
        model = Message
        fields = ("text",)
        widgets = {
            "text": forms.Textarea(attrs={
                "placeholder": "Enter message",
                "class": "message-textarea",
                "rows": 4,
                "cols": 40,
            }),
        }
        labels = {
            "text": "New message"
        }


class NewAd(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data["available_now"] and \
                not cleaned_data.get("available_from"):
            self.add_error("available_from", "Date field is mandatory if "
                                             "not available now")
        elif cleaned_data["available_now"]:
            cleaned_data["available_from"] = None

    def clean_title(self):
        value: str = self.cleaned_data['title']
        return value.title()

    def clean_city(self):
        value: str = self.cleaned_data['city']
        return value.title()

    class Meta:
        model = Ad
        fields = ("title", "city", "description", "price",
                  "furniture", "rooms", "available_now",
                  "available_from", "image")
        widgets = {
            "description": forms.Textarea(attrs={
                "placeholder": "Enter description",
                "class": "message-textarea",
                "rows": 4,
                "cols": 20,
            }),
            "available_from": forms.DateInput(format='%d/%m/%Y',
                                              attrs={'type': 'date'})
        }
        labels = {
            "description": "Description"
        }
        error_messages = {
            'price': {
                'min_value': "Price cannot be less than 1.00$",
            },
            'rooms': {
                'min_value': "Number of rooms cannot be less then 1",
            }
        }
