from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.forms import ModelForm, HiddenInput
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Count
from django.http.response import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .models import User, Post, Follower


def index(request):
    context = {}
    if request.user.is_authenticated:
        form = PostForm()
        context['form'] = form

    page_num = request.GET.get('page')
    if page_num is None:
        page_num = 1
    # get posts from database
    posts = Post.objects.all().annotate(likes=Count('likers')).order_by('-created')
    posts_paginator = Paginator(posts, 10)
    page = posts_paginator.get_page(page_num)
    context['page'] = page
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
            return render(request, "network/login.html",
                          {"message": "Invalid username and/or password."})
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
            return render(request, "network/register.html",
                          {"message": "Passwords must match."})

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html",
                          {"message": "Username already taken."})
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
        self.fields['post'].widget.attrs.update({'autofocus': 'autofocus'})


@login_required
def post(request):
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
            return HttpResponseRedirect(reverse('index'))
        message = 'Something went wrong =(. Please check your form data.'
        return render(request, "network/index.html", {
            'form': form,
            'message': message
        })
    return render(request, "network/index.html", {'form': PostForm()})


def user(request, user_id):
    context = {}
    try:
        user = User.objects.get(pk=user_id)
    except:
        return HttpResponseRedirect(reverse('index'))
    context['user_'] = user
    context['followers_count'] = user.followers.count()
    context['following_count'] = user.following.count()

    # TODO: should really factor out this functionality because it's used in
    # multiple places
    page_num = request.GET.get('page')
    if page_num is None:
        page_num = 1
    # get posts from database
    posts = user.posts.order_by('-created').annotate(
        likes=Count('likers'))
    posts_paginator = Paginator(posts, 10)
    page = posts_paginator.get_page(page_num)
    context['page'] = page
    # check if the user is already following this person
    if user.is_authenticated:
        following = user.followers.filter(follower=request.user).exists()
        context['following'] = following
    # breakpoint()
    return render(request, "network/user.html", context)

# TODO: fix this
@csrf_exempt
def follow(request, user_id):
    # check for a PUT request
    if request.method != 'PUT':
        return JsonResponse({"error": "PUT request required."}, status=400)
    # ensure user.id != user_id
    if request.user.id == int(user_id):
        return JsonResponse({"error": "You cannot follow yourself."},
                            status=400)

    # retrieve users
    followed = User.objects.filter(pk=int(user_id))
    follower = User.objects.filter(pk=request.user.id)
    if not (followed.exists() and follower.exists()):
        return JsonResponse({"error": "These users do not exist."}, status=400)
    else:
        followed = followed[0]
        follower = follower[0]

    # if follow link is in the database, remove it
    action = None
    if Follower.objects.filter(followed=followed, follower=follower).exists():
        Follower.objects.filter(followed=followed, follower=follower).delete()
        action = 'Unfollowed'
    # else add it
    else:
        Follower.objects.create(followed=followed,
                                follower=follower)
        action = 'Followed'
    return JsonResponse({'action': action}, status=200)

@login_required
def following(request):
    # get following list
    # TODO: determine if there is a better way to retrieve the actual users
    following_list = request.user.following.all().values_list('followed', flat=True)
    following_list = User.objects.filter(id__in=following_list)
    context = {}
    page_num = request.GET.get('page')
    if page_num is None:
        page_num = 1
    # get posts from these users
    posts = Post.objects.filter(poster__in=following_list).annotate(likes=Count('likers')).order_by('-created')
    posts_paginator = Paginator(posts, 10)
    page = posts_paginator.get_page(page_num)
    context['page'] = page
    return render(request, "network/following.html", context)