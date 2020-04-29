from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver
from cloudinary.models import CloudinaryField

from django.db import models



class Category(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "categories"
        ordering = ['title',]


class Item(models.Model):
    LOCATION_CHOICES = (
        ('AUH', 'Abu Dhabi'),
        ('AJM', 'Ajman'),
        ('SHJ', 'Sharjah'),
        ('DXB', 'Dubai'),
        ('FUJ', 'Fujairah'),
        ('RAK', 'Ras Al Khaimah'),
        ('UAQ', 'Umm Al Quwain'),
    )
    TYPE_CHOICES = (
        ('free', 'Free (I want to give something away)'),
        ('wanted', 'Wanted (I want to get something)'),
    )
    STATUS_CHOICES = (
        ('available', 'Available'),
        ('completed', 'Completed'),
        ('awaiting', 'Awaiting Pickup'),
        ('onhold', 'On Hold'),
        ('removed', 'Removed'),
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    category = models.ForeignKey(Category, blank=True, null=True)
    other_category = models.CharField(max_length=128, blank=True, default="")
    details = models.TextField(blank=True, default="")
    posted_on = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, related_name='item_user')
    completed_with = models.ForeignKey(User, blank=True, null=True, related_name='item_completed_with')
    location_detail = models.CharField(max_length=255, blank=True, null=True)

    # Cloudinary
    image1 = CloudinaryField('image', blank=True, null=True, default='')
    image2 = CloudinaryField('image', blank=True, null=True, default='')
    image3 = CloudinaryField('image', blank=True, null=True, default='')

    location = models.CharField(
        max_length=3,
        choices=LOCATION_CHOICES,
        default='DXB',
    )
    post_type = models.CharField(
        max_length=6,
        choices=TYPE_CHOICES,
        default='free',
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='available',
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-posted_on',]

    def get_absolute_url(self):
        return reverse("items:detail", kwargs={"pk":self.pk, "slug":self.slug})

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Item, self).save(*args, **kwargs)


class Activity(models.Model):
    TYPE_CHOICES = (
        ('available', 'Available'),
        ('offered', 'Offered'),
        ('requested', 'Requested'),
        ('awaiting', 'Awaiting Pickup'),
        ('completed', 'Completed'),
    )
    item = models.ForeignKey(Item, blank=True, null=True)
    user = models.ForeignKey(User, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    change_type = models.CharField(
        max_length=9,
        choices=TYPE_CHOICES,
        blank=True,
        default='',
    )

    def __str__(self):
        return self.item.name

    class Meta:
        verbose_name_plural = "activities"


class UserMessage(models.Model):
    TAG_CHOICES = (
        ('request', 'Request'),
        ('offer', 'Offer'),
        ('question', 'Question'),
        ('report', 'Report'),
        ('reply', 'Reply'),
    )
    from_user = models.ForeignKey(User, related_name="usermessages")
    to_user = models.ForeignKey(User)
    item = models.ForeignKey(Item)
    date = models.DateTimeField(auto_now_add=True)
    pickup_time = models.CharField(max_length=255, blank=True, null=True)
    message = models.TextField()
    related_to = models.ForeignKey('self', blank=True, null=True)
    tag = models.CharField(
        max_length=9,
        choices=TAG_CHOICES,
        blank=True,
        default='request',
    )

    def __str__(self):
        return self.message

    class Meta:
        ordering = ['-date',]


class Profile(models.Model):
    LOCATION_CHOICES = (
        ('AUH', 'Abu Dhabi'),
        ('AJM', 'Ajman'),
        ('SHJ', 'Sharjah'),
        ('DXB', 'Dubai'),
        ('FUJ', 'Fujairah'),
        ('RAK', 'Ras Al Khaimah'),
        ('UAQ', 'Umm Al Quwain'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    last_message_check = models.DateTimeField(blank=True, null=True)
    location = models.CharField(
        max_length=3,
        choices=LOCATION_CHOICES,
        default='DXB',
    )

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if not instance.is_superuser:
        instance.profile.save()
