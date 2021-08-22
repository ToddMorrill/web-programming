from typing import List
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError, models
from django.forms import ModelForm
from django.http import HttpResponse, HttpResponseRedirect

from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from .models import Listing, User, Listing, Watchlist, Bid


def index(request):
    # get active listings
    listings = Listing.objects.filter(winner__isnull=True)
    # TODO: figure out how to join in all these max bids
    # get current bid prices
    highest_bids = Bid.objects.values('listing').annotate(highest_bid=models.Max('price'))
    updated_listings = []
    for listing_ in listings:
        for bid in highest_bids:
            if (bid['listing'] == listing_.id) and (bid['highest_bid'] is not None):
                listing_.price = bid['highest_bid'] 
        updated_listings.append(listing_)
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
            return render(request, "auctions/login.html",
                          {"message": "Invalid username and/or password."})
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
            return render(request, "auctions/register.html",
                          {"message": "Passwords must match."})

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html",
                          {"message": "Username already taken."})
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


class ListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'price', 'image_url', 'category']

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


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
                return render(request, 'auctions/create.html', {
                    'form': form,
                    'message': message
                })
            return HttpResponseRedirect(
                reverse('listing', args=(instance.pk, )))
        message = 'Something went wrong =(. Please check your form data.'
        return render(request, 'auctions/create.html', {
            'form': form,
            'message': message
        })
    return render(request, 'auctions/create.html', {'form': ListingForm()})


def listing(request, listing_id):
    context = {}
    # notifies user of success/failure adding to the watchlist
    if 'message' in request.session:
        context['message'] = request.session['message']
        # delete this message so it isn't accidentally used later
        del request.session['message']
    listing_ = Listing.objects.get(pk=listing_id)

    # update the "price" with the highest bid
    highest_bid = Bid.objects.filter(listing=listing_id).aggregate(models.Max('price'))
    if highest_bid['price__max']:
        listing_.price = highest_bid['price__max']
    context['listing'] = listing_

    # check if user has this listing on their watchlist
    on_watchlist = Watchlist.objects.filter(user=request.user,
                                            listing=listing_id).exists()
    context['on_watchlist'] = on_watchlist

    # create a bid form
    context['form'] = BidForm
    return render(request, 'auctions/listing.html', context)


@login_required
def watchlist(request, listing_id):
    # TODO: this should probably be converted to a form and POST request
    listing = get_object_or_404(Listing, pk=listing_id)

    # if user has already added this item, remove it
    if Watchlist.objects.filter(user=request.user,
                                listing=listing_id).exists():
        # remove the item
        Watchlist.objects.filter(user=request.user,
                                 listing=listing_id).delete()
        message = "Successfully removed this item from your watchlist."
        messages.add_message(request, messages.SUCCESS, message)
        request.session['message'] = message
        return HttpResponseRedirect(reverse('listing', args=(listing_id, )))

    # get watchlist for user, create it if it doesn't exist
    user_watchlist, created = Watchlist.objects.get_or_create(
        user=request.user)
    user_watchlist.listing.add(listing)
    message = "Successfully added this item to your watchlist."
    messages.add_message(request, messages.SUCCESS, message)
    request.session['message'] = message
    return HttpResponseRedirect(reverse('listing', args=(listing_id, )))


class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ['price']

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        self.fields['price'].label = 'Enter your bid here'

@login_required
def bid(request, listing_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    
    if request.method == 'POST':
        listing = Listing.objects.get(pk=listing_id)
        # if winner already declared, notify user
        if listing.winner:
            message = f'This auction is closed!'
            request.session['message'] = message
            return HttpResponseRedirect(reverse('listing', args=(listing_id,)))

        # create form with data entered
        form = BidForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            # add listing and bidder information
            listing = Listing.objects.get(pk=listing_id)
            instance.listing = listing
            instance.bidder = request.user

            # check that the bid is greater than starting price and highest bid
            bid = Bid.objects.filter(listing=listing_id).aggregate(models.Max('price'))
            highest_bid = bid['price__max'] if bid['price__max'] is not None else 0
            if not instance.price > listing.price:
                message = f'The bid must be higher than the starting price of ${listing.price:,.2f}.'
                request.session['message'] = message
                return HttpResponseRedirect(reverse('listing', args=(listing_id,)))
            elif not instance.price > highest_bid:
                message = f'The bid must be higher than the current price of ${highest_bid:,.2f}.'
                request.session['message'] = message
                return HttpResponseRedirect(reverse('listing', args=(listing_id,)))

            # enter listing into database
            try:
                instance.save()
                message = 'Bid placed successfully!'
            except IntegrityError:
                message = 'There was an issue creating the bid!.'
                pass
            request.session['message'] = message
            return HttpResponseRedirect(reverse('listing', args=(listing_id,)))
        message = 'Something went wrong =(. Please check your form data.'
        return render(request, 'auctions/create.html', {
            'form': form,
            'message': message
        })
    return HttpResponseRedirect(reverse('listing', args=(listing_id, )))

@login_required
def close(request, listing_id):
    # TODO: this should probably be converted to a form and POST request
    # confirm user is the lister
    listing = Listing.objects.get(pk=listing_id)
    if request.user != listing.lister:
        return HttpResponse('401: Unauthorized', status=401)
    if listing.winner:
        message = f'This auction is already closed!'
        request.session['message'] = message
        return HttpResponseRedirect(reverse('listing', args=(listing_id,)))
    # get the user with the highest bid
    # TODO: determine if there is better logic to do this
    listing_bids = Bid.objects.filter(listing=listing_id)
    max_bid = 0
    max_record = None
    for record in listing_bids:
        if record.price > max_bid:
            max_bid = record.price
            max_record = record
    listing.winner = max_record.bidder
    listing.save()
    return HttpResponseRedirect(reverse('listing', args=(listing_id, )))
