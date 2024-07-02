from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Bid(models.Model):
    owner  = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    amount = models.IntegerField()
    
    def __str__(self):
        return f"{self.owner} {self.amount}"

class Listing(models.Model):
    owner        = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    title        = models.CharField(max_length=32)
    description  = models.TextField(max_length=1024)
    starting_bid = models.IntegerField()
    current_bid  = models.ForeignKey(Bid, on_delete=models.SET_NULL, null=True, blank=True, related_name="listing")
    image        = models.URLField(blank=True)
    category     = models.CharField(max_length=32, blank=True)
    status       = models.CharField(max_length=6, null=True) #either active or closed
    winner       = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="winnings")
    winner_name  = models.CharField(max_length=64, null=True, blank=True)
    
    def __str__(self):
        return f"{self.owner} {self.title}"

class Comment(models.Model):
    author  = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    listing = models.ForeignKey(Listing, null=True, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField(max_length=512)
    
    def __str__(self):
        return f"{self.author} {self.content}"

class Wish(models.Model):
    owner   = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist")
    listing = models.ForeignKey(Listing, null=True, on_delete=models.CASCADE, related_name="watchlist")

    def __str__(self):
        return f"{self.owner} {self.listing}"
