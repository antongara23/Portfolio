from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.core.validators import MinValueValidator, FileExtensionValidator
from django.utils import timezone


def validate_date(value):
    """Validate if date is not earlier than current"""
    if value < timezone.now().date():
        raise ValidationError("The chosen date must be today or later",
                              code="min_value")


class User(AbstractUser):
    mobile_phone = models.CharField(max_length=20, blank=True, null=True)
    saved = models.ManyToManyField("Ad", blank=True, related_name="saved_by")


class Ad(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="user_ad")
    city = models.CharField(max_length=32)
    title = models.CharField(max_length=64)
    description = models.TextField(max_length=1000)
    price = models.DecimalField(max_digits=8, decimal_places=2,
                                validators=[MinValueValidator(1)])
    furniture = models.BooleanField(default=False)
    rooms = models.IntegerField(validators=[MinValueValidator(1)])
    available_now = models.BooleanField(default=True)
    available_from = models.DateField(default=None, null=True, blank=True,
                                      validators=[validate_date])
    creation_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(default=None, null=True, blank=True)
    is_actual = models.BooleanField(default=True)
    image = models.ImageField(default=None, null=True, blank=True,
                              upload_to="ad_images",
                              validators=[FileExtensionValidator(
                                  ['jpg', 'jpeg', 'png', 'gif'])])

    def __str__(self):
        return f"{self.id} {self.user}, {self.city}, active={self.is_actual}"


class Dialog(models.Model):
    initiator = models.ForeignKey(User, on_delete=models.CASCADE,
                                  related_name="initiated_dialogs")
    recipient = models.ForeignKey(User, on_delete=models.CASCADE,
                                  related_name="received_dialogs")
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE,
                           related_name="related_dialogs")
    creation_date = models.DateTimeField(auto_now_add=True)
    initiator_read = models.BooleanField(default=True)
    recipient_read = models.BooleanField(default=False)

    def clean(self):
        if self.initiator == self.ad.user:
            raise ValidationError("The initiator cannot be the author of the ad.")
        if self.initiator == self.recipient:
            raise ValidationError("The initiator and recipient cannot be the same user.")

    class Meta:
        unique_together = ('initiator', 'recipient', 'ad')

    def __str__(self):
        return f"{self.initiator} : {self.recipient} on ({self.ad})"


class Message(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="user_message", null=True,
                               blank=True)
    dialog = models.ForeignKey(Dialog, on_delete=models.CASCADE,
                               related_name="dialog_messages", null=True,
                               blank=True)
    text = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author} on dialog ({self.dialog}). {self.creation_date}"
