from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import Bid, Comment, Listing, User, Watch

def index(request):
    listings = Listing.objects.filter(sold=False)
    
    return render(request, "auctions/index.html", {
        "listings": listings,
        "mode": "active",
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


@login_required
def listing(request, id):
    
    listing = Listing.objects.get(id=id)
    
    user = request.user
    is_owner = False 
    if listing.user == user:
        is_owner = True
    
    
    bids = Bid.objects.filter(listing=listing)
    last_bid = bids.last()
    watch_list_user = Watch.objects.filter(user=user, listing=listing)

    on_watch_list = False
    invalid_bid = False
    
    if request.method == "POST":      
        # Comment
        if "comment" in request.POST:
            comment = request.POST["comment"]
            if comment != "":
                Comment.objects.create(user = user, comment = comment, listing = listing)
        # Bidding
        elif "bid" in request.POST:
            bid = request.POST["bid"]
            if last_bid is None:
                if float(bid) > listing.price:
                    Bid.objects.create(user=user, amount=bid, listing=listing)
                    auction_to_add = Listing.objects.get(id=id)
                    auction_to_add.bid = bid
                    auction_to_add.save()
                else:
                    invalid_bid = True
            elif float(bid) > last_bid.amount:
                Bid.objects.create(user=user, amount=bid, listing=listing)
                auction_to_add = Listing.objects.get(id=id)
                auction_to_add.bid = bid
                auction_to_add.save()
            else:
                invalid_bid = True
        # Add to WatchList
        elif "watchlist" in request.POST:
            Watch.objects.create(listing=listing, user=user)
        # Remove WatchList
        elif "remove_watchlist" in request.POST:
            watch_list_user.first().delete()
        # Close
        else:
            close_bidding(request, id)
    
    if len(watch_list_user) == 1:
        on_watch_list = True

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "bids": Bid.objects.filter(listing=listing),
        "last_bid": Bid.objects.filter(listing=listing).last(),
        "comments": Comment.objects.filter(listing=listing.id), 
        "is_owner": is_owner,
        "on_watch_list": on_watch_list,
        "no_of_comments": len(Comment.objects.filter(listing=listing.id)),
        "invalid_bid":invalid_bid
    })


@login_required
def create_listing(request):
    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        price = request.POST["price"]
        image_url = request.POST["image_url"]

        user = request.user
        category = request.POST["category"]
        Listing.objects.create(user = user, title = title, description = description, 
            price = price, image_url = image_url, category = category, sold=False)
        
        return HttpResponseRedirect(reverse("index"))

    else:
        return render(request, "auctions/create_listing.html")


def category(request, category):
    listings = Listing.objects.filter(category=category, sold=False)
    
    return render(request, "auctions/index.html", {
        "listings": listings,
        "mode": category
    })

def categories(request):
    return render(request, "auctions/categories.html")

@login_required
def close_bidding(request, id):
    
    listing = Listing.objects.get(id=id)
    
    user = request.user
    is_owner = False 
    if listing.user == user:
        is_owner = True
    
    
    bids = Bid.objects.filter(listing=listing)
    last_bid = bids.last()
    watch_list_user = Watch.objects.filter(user=user, listing=listing)

    invalid_bid = False
    on_watch_list = False
    if len(watch_list_user) == 1:
        on_watch_list = True

    listing.sold = True
    listing.save()

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "bids": Bid.objects.filter(listing=listing),
        "last_bid": last_bid,
        "no_of_comments": len(Comment.objects.filter(listing=listing.id)),
        "comments": Comment.objects.filter(listing=listing.id), 
        "is_owner": is_owner,
        "on_watch_list": on_watch_list,
        "invalid_bid": invalid_bid
        
    })

def inactive(request):
    listings = Listing.objects.filter(sold=True)
    
    return render(request, "auctions/index.html", {
        "listings": listings,
         "mode": "inactive"
    })

@login_required
def watchlist(request):
    watch_list = Watch.objects.filter(user=request.user)
    
    return render(request, "auctions/watchlist.html", {
        "watch_list": watch_list
    })