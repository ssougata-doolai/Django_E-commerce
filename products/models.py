from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import reverse

CATAGORY_CHOICE = (
    ('Hand Loom',' Hand Loom'),
    ('Silk','Silk'),
    ('Tat','Tat'),
    ('Jamdani','Jamdani')
)

LABEL_CHOICE = (
    ('Primary','primary'),
    ('Secondary','secondary'),
    ('Danger','danger')
)
class Item(models.Model):
    title = models.CharField(max_length = 100)
    price = models.DecimalField(max_digits = 100, decimal_places = 2)
    discount_price = models.DecimalField(max_digits = 100, decimal_places = 2,blank=True, null = True)
    catagory =  models.CharField(max_length = 10, choices = CATAGORY_CHOICE)
    label = models.CharField(max_length = 10, choices = LABEL_CHOICE)
    slug = models.SlugField(unique = True)
    description = models.TextField()
    quantity = models.IntegerField(default=1)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now = False, auto_now_add = True)
    updated = models.DateTimeField(auto_now = True, auto_now_add = False)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("products:product", kwargs={
            'slug':self.slug
        })

class ItemImage(models.Model):
    item = models.ForeignKey(Item, on_delete = models.CASCADE)
    image = models.ImageField(upload_to = 'products/images/')
    featured = models.BooleanField(default = False)
    thumbnail = models.BooleanField(default = False)
    active = models.BooleanField(default = True)
    updated = models.DateTimeField(auto_now = True, auto_now_add = False)

    def __str__(self):
        return self.item.title

class Variation(models.Model):
    title = models.CharField(max_length = 100)
    item = models.ForeignKey(Item, on_delete = models.CASCADE)
    image = models.ForeignKey(ItemImage, on_delete = models.CASCADE, null=True, blank = True)
    price = models.DecimalField(max_digits = 100, decimal_places = 2,blank=True, null = True)
    active = models.BooleanField(default = True)
    updated = models.DateTimeField(auto_now = True, auto_now_add = False)

    def __str__(self):
        return self.title
