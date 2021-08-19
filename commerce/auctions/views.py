from typing import List
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.forms import ModelForm
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from .models import Listing, User, Listing, Watchlist


def index(request):
    # get active listings
    listings = Listing.objects.all()
    return render(request, "auctions/index.html", {'listings': listings})


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

class ListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'price', 'image_url', 'category']

@login_required
def create_listing(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    if request.method == 'POST':
        # create form with data entered
        form = ListingForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            # add lister information
            instance.lister = request.user
            # enter listing into database
            try:
                instance.save()
            except IntegrityError:
                message = f'Title: "{instance.title}" already exists. Please create a new title.'
                return render(request, 'auctions/create.html', {'form': form, 'message': message})
            return HttpResponseRedirect(reverse('listing', args=(instance.pk,)))
        message = 'Something went wrong =(. Please check your form data.'
        return render(request, 'auctions/create.html', {'form': form, 'message': message})
    return render(request, 'auctions/create.html', {'form': ListingForm()})

def listing(request, listing_id):
    listing_ = Listing.objects.get(pk=listing_id)
    return render(request, 'auctions/listing.html', {'listing': listing_})

@login_required
def watchlist(request, listing_id):
    # TODO: notify user of success or failure
    listing = get_object_or_404(Listing, pk=listing_id)
    
    # check if user has already added this item
    if Watchlist.objects.filter(user=request.user, listing=listing_id).exists():
        messages.add_message(request, messages.ERROR, "You have already added this item to your watchlist.")
        return HttpResponseRedirect(reverse('listing', args=(listing_id,)))
    
    # get watchlist for user, create it if it doesn't exist
    user_watchlist, created = Watchlist.objects.get_or_create(user=request.user)
    user_watchlist.listing.add(listing)
    messages.add_message(request, messages.SUCCESS, "Successfully added this item to your watchlist.")
    return HttpResponseRedirect(reverse('listing', args=(listing_id,)))
