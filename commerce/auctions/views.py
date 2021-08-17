from typing import List
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.forms import ModelForm
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import Listing, User


def index(request):
    return render(request, "auctions/index.html")


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