from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listing(models.Model):
    
    title = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    image_url = models.TextField(null=True, blank=True)

    description = models.TextField()

    bid = models.DecimalField(max_digits=12, decimal_places=2 , blank=True, null=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.CharField(max_length=20)

    sold = models.BooleanField(default=False)


class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listings")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")


class Comment(models.Model):
    comment = models.TextField()
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")


class Watch(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watch_list")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="watch_list")

