from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms

from .models import User, Listing, Comment, Wish, Bid

category_choices=[
        ("electronics", "Electronics"),
        ("fashion"    , "Fashion"    ),
        ("home"       , "Home"       ),
        ("toys"       , "Toys"       ),
        ("other"      , "Other"      ),
    ]

class NewListingForm(forms.Form):
    title        = forms.CharField   (label = "", widget=forms.TextInput  (attrs={"placeholder" : "Page Title"}))
    description  = forms.CharField   (label = "", widget=forms.Textarea   (attrs={"placeholder" : "Place your description here!", "style": "height: 550px; margin-top: 30px;"}))
    starting_bid = forms.IntegerField(label = "", widget=forms.NumberInput(attrs={"placeholder" : "Desired Starting Bid"}))
    image        = forms.URLField    (label="", required=False, widget=forms.URLInput(attrs={"placeholder": "Image URL"}))
    category     = forms.ChoiceField (label="", required=False, choices=category_choices)

class NewCommentForm(forms.Form):
    content = forms.CharField(label = "", widget=forms.Textarea(attrs={
        "placeholder" : "Type your comment here!",
        "style": "height: 30px; min-height: 30px;"}))

class BidForm(forms.Form):
    amount = forms.IntegerField(label="", widget=forms.NumberInput(attrs={"placeholder": "Bid Amount"}))

    #ability to pass parameters to a form (stack overflow): https://stackoverflow.com/questions/14660037/django-forms-pass-parameter-to-form
    def __init__(self,*args,**kwargs):
        min_value = kwargs.pop("min_value")
        super(BidForm,self).__init__(*args,**kwargs)
        self.fields["amount"].widget.attrs.update({'min': min_value})

def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.exclude(status="closed")
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
    
def listing(request, listing_id):
    listing_ = Listing.objects.get(pk=listing_id)
    is_in_watchlist = request.user.is_authenticated and Wish.objects.filter(owner=request.user, listing=listing_).exists()
    if listing_.current_bid is None: min_val = listing_.starting_bid
    else :                           min_val = listing_.current_bid.amount + 1

    if request.method == "POST":
        action = request.POST.get("action")
        #the actions you can do on a listing are: commenting, bidding (if you don't own it), and closing (if you do own it)
        if action == "comment":
            form = NewCommentForm(request.POST)
            if form.is_valid():
                content_ = form.cleaned_data["content"]
                new_comment = Comment.objects.create(
                    author  = request.user,
                    content = content_,
                    listing = listing_
                )
        elif action == "bid":
            form = BidForm(request.POST, min_value=min_val)
            if form.is_valid():
                bid_amount = form.cleaned_data["amount"]
                new_bid = Bid.objects.create(
                    owner       =request.user,
                    amount      =bid_amount
                )
                listing_.current_bid = new_bid
                listing_.save()
        elif action == "close":
            listing_.status = "closed"
            if listing_.current_bid != None:
                listing_.winner      = listing_.current_bid.owner
                listing_.winner_name = listing_.current_bid.owner.get_username()
            listing_.save()
    return render(request, "auctions/listing.html", {
        "listing": listing_,
        "comments": listing_.comments.all(),
        "comment_form": NewCommentForm(),
        "is_in_watchlist": is_in_watchlist,
        "bid_form": BidForm(min_value=min_val)
    })

def create_listing(request):
    if request.method == "POST":
        form = NewListingForm(request.POST)
        if form.is_valid():
            title_        = form.cleaned_data["title"]
            description_  = form.cleaned_data["description"]
            starting_bid_ = form.cleaned_data["starting_bid"]
            #current_bid_ = form.cleaned_data["current_bid"]
            image_        = form.cleaned_data["image"]
            category_     = form.cleaned_data["category"]
            
            new_listing = Listing.objects.create(
                owner       =request.user,
                title       =title_,
                description =description_,
                starting_bid=starting_bid_,
                current_bid = None,
                image       =image_,
                category    =category_,
                status      ="active",
                winner      = None,
                winner_name = None
            )
        return listing(request, new_listing.id)
    return render(request, "auctions/create.html", {
        "form": NewListingForm()
    })

def watchlist(request):
    return render(request, "auctions/watchlist.html", {
        "watchlist": request.user.watchlist.all()
    })

def watch(request, listing_id):
    listing_ = Listing.objects.get(pk=listing_id)
    
    if request.method == "POST":
        action = request.POST.get("action")

        if action == "add":
            new_wish = Wish.objects.create(
                owner = request.user,
                listing = listing_
            )
        elif action == "remove":
            Wish.objects.filter(owner=request.user, listing=listing_).delete()
    return listing(request, listing_id)

def categories(request):
    return render(request, "auctions/categories.html", {
        "categories": category_choices
    })

def category(request, category_choice):
    return render(request, "auctions/category.html", {
        "listings": Listing.objects.filter(category=category_choice),
        "category": category_choice.capitalize()
    })