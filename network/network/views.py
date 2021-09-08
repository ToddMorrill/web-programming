from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.forms import ModelForm, HiddenInput
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Post


def index(request):
    context = {}
    if request.user.is_authenticated:
        form = PostForm()
        context['form'] = form
    return render(request, "network/index.html", context)


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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


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
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['post']
        widgets = {'poster': HiddenInput()}

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        self.fields['post'].label = ''

@login_required
def posts(request):
    # process POST request
    if request.method == 'POST':
        # create form with data entered
        form = PostForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            # add lister information
            instance.poster = request.user
            # enter listing into database
            instance.save()
            return HttpResponseRedirect(
                reverse('index'))
        message = 'Something went wrong =(. Please check your form data.'
        return render(request, "network/index.html", {
            'form': form,
            'message': message
        })
    return render(request, "network/index.html", {'form': PostForm()})