from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
import datetime
import json

from .models import User, Post, UserFollower, UserFollowing

def index(request):
    posts = Post.objects.all()

    # put posts in reverse chronological order
    posts_reversed = []
    for post in posts:
        try: # this checks if the user has liked the post or not
            user = post.liked_by.get(pk=int(request.user.id))
            post.liked = True
        except:
            post.liked = False

        post.likes = len(post.liked_by.all())
        posts_reversed.insert(0, post)
    
    # pagination
    if len(posts_reversed) <= 10: # is pagination required? i.e. are there more than 10 posts
        paginationRequired = False
    else:
        paginationRequired = True
        pages = Paginator(posts_reversed, 10)
        try: # check if the 'page' query is passed
            page_num = int(request.GET["page"])
            paginationPosts = pages.page(page_num)
            
        except:
            # default to page 1 if no 'page' query is passed
            paginationPosts = pages.page(1)
    
    
        hasPrevious = paginationPosts.has_previous()
        hasNext = paginationPosts.has_next()
    
        previousPage = paginationPosts.number # use the current page number as default
        if hasPrevious:
            previousPage = paginationPosts.previous_page_number()
        
        nextPage = paginationPosts.number # use the current page number as default
        if hasNext:
            nextPage = paginationPosts.next_page_number()

        data = {
            'posts': paginationPosts,
            'pages': pages,
            'previous': hasPrevious,
            'next': hasNext,
            'previousPage': previousPage,
            'nextPage': nextPage
        }
    
    # this value changes depending on if there are enough posts for pagination, hence why it is outside the if/else statement
    data["paginationRequired"] = paginationRequired

    return render(request, "network/index.html", data)

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
            new_user = User.objects.get(username=username)
            following = UserFollowing(user_id=new_user)
            following.save()
            followers = UserFollower(user_id=new_user)
            followers.save()

        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


def createPost(request):
    if request.method != "POST":
        return HttpResponseRedirect(reverse("index"))
    else:
        # create the new post
        content = request.POST["content"]
        timeDate = f"{datetime.datetime.now().date()} {datetime.datetime.now().time()}"
        user = request.user.username
        newPost = Post(
            text=content,
            time_date=timeDate,
            likes=0,
            owner=user
        )
        newPost.save()
        return HttpResponseRedirect("/")

def likeInteraction(request, post_id):
    # all status codes sent back are inline with industry standards, i.e. 400 = user error, 500 = server error, etc.

    # check if the user is logged in
    if not request.user.is_authenticated:
        return HttpResponse(300)

    # check if the POST method was used, if it wasn't the the user would have been editing the code
    if request.method != "POST":
        return HttpResponse(400)

    try:
        # get the post
        post = Post.objects.get(pk=int(post_id))
        try: # if succesful, the user will be found and removed (i.e. unliking the post)
            user = post.liked_by.get(pk=int(request.user.id))
            post.liked_by.remove(user)
            return HttpResponse(202)
        except: # if unsuccesful, the user will be added (i.e. liking the post)
            try:
                post.liked_by.add(request.user)
                return HttpResponse(200)
            except:
                return HttpResponse(500)
    except:
        return HttpResponse(500)


def showProfile(request, name):
    try: # does the user exist
        profile = User.objects.get(username=name)
        # get who the profile follows and the profiles followers
        # following & followers have their own database model - and not part of the user model
        xx = UserFollowing.objects.get(pk=int(profile.id))
        yy = UserFollower.objects.get(pk=int(profile.id))
        following = len(xx.following.all())
        followers = len(yy.followers.all())

        user_posts = []
        post_error = False
        try: # can the user's posts be retrieved
            fetched_posts = Post.objects.filter(owner=name)
            for post in fetched_posts:
                try: # has the user liked the post?
                    user = post.liked_by.get(pk=int(request.user.id))
                    post.liked = True
                except:
                    post.liked = False

                post.likes = len(post.liked_by.all())
                user_posts.insert(0, post)
        except:
            post_error = True

        data = {
            "profile": profile,
            "following": following,
            "followers": followers,
            "post_error": post_error
        }

        # pagination
        if len(user_posts) <= 10: # skip pagination if there are 10 posts or less
            paginationRequired = False
            data["posts"] = user_posts
        else:
            paginationRequired = True
            pages = Paginator(user_posts, 10)
            try: # check if the 'page' query is passed
                page_num = int(request.GET["page"])
                paginationPosts = pages.page(page_num)
            except:
                # use page 1 by default
                paginationPosts = pages.page(1)
        
            # is there a previous & next page
            hasPrevious = paginationPosts.has_previous()
            hasNext = paginationPosts.has_next()

            previousPage = paginationPosts.number # use the current page as a default
            if hasPrevious:
                previousPage = paginationPosts.previous_page_number()
            nextPage = paginationPosts.number # use the current page as a default
            if hasNext:
                nextPage = paginationPosts.next_page_number()

            data["posts"] = paginationPosts
            data["pages"] = pages
            data["previous"] = hasPrevious
            data["next"] = hasNext
            data["previousPage"] = previousPage
            data["nextPage"] = nextPage
        
        # this value changes depending on if there are enough posts for pagination, hence why it is outside the if/else statement
        data["paginationRequired"] = paginationRequired

        if request.user.is_authenticated:
            following = UserFollowing.objects.get(pk=int(request.user.id)).following.all()
            if profile in following: # does the logged in user follow the profile
                data["isFollowing"] = True
            else:
                data["isFollowing"] = False
        
        return render(request, "network/profile.html", data)

    except:
        return render(request, "network/profile.html", {"warning": True})

def following(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    
    currentUser = User.objects.get(pk=int(request.user.id))
    following = UserFollowing.objects.get(pk=int(currentUser.id)).following.all()
    
    allPosts = Post.objects.all()
    posts = []
    for post in allPosts:
        for owner in following:
            if post.owner == owner.username:
                try: # has the user liked the post?
                    user = post.liked_by.get(pk=int(request.user.id))
                    post.liked = True
                except:
                    post.liked = False

                post.likes = len(post.liked_by.all())
                posts.insert(0, post)
                continue # skip this owner, no need to check multiple times

    data = {
        "posts": posts
    }

    # pagination
    if len(posts) <= 10: # skip pagination if there are 10 posts or less
        paginationRequired = False
    else:
        paginationRequired = True
        pages = Paginator(posts, 10)
        try: # check if the 'page' query is passed
            page_num = int(request.GET["page"])
            paginationPosts = pages.page(page_num)
            
        except:
            paginationPosts = pages.page(1) # use page 1 as default if no query is passed
    
        # check for a previous & next page
        hasPrevious = paginationPosts.has_previous()
        hasNext = paginationPosts.has_next()
        
        previousPage = paginationPosts.number # use current page as default
        if hasPrevious:
            previousPage = paginationPosts.previous_page_number()
        
        nextPage = paginationPosts.number # use current page as default
        if hasNext:
            nextPage = paginationPosts.next_page_number()

        data["posts"] =  paginationPosts
        data["pages"] =  pages
        data["previous"] =  hasPrevious
        data["next"] =  hasNext
        data["previousPage"] =  previousPage
        data["nextPage"] =  nextPage

    # this value changes depending on if there are enough posts for pagination, hence why it is outside the if/else statement
    data["paginationRequired"] = paginationRequired

    return render(request, "network/following.html", data)

def followUser(request, name):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    # get the profile and the user
    profile = User.objects.get(username=name)
    currentUser = User.objects.get(pk=int(request.user.id))
    
    followers = UserFollower.objects.get(pk=int(profile.id)) # who follows the profile
    following = UserFollowing.objects.get(pk=int(currentUser.id)) # who the logged in user follows

    # add the user & profile to the followers/following lists respectively
    followers.followers.add(currentUser)
    following.following.add(profile)

    return HttpResponseRedirect(f"/profile/{name}")

def unfollowUser(request, name):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    # get the profile and the user
    profile = User.objects.get(username=name)
    currentUser = User.objects.get(pk=int(request.user.id))
    
    followers = UserFollower.objects.get(pk=int(profile.id)) # who follows the profile
    following = UserFollowing.objects.get(pk=int(currentUser.id)) # who the logged in user follows

    # remove the user & profile to the followers/following lists respectively
    followers.followers.remove(currentUser)
    following.following.remove(profile)
        
    return HttpResponseRedirect(f"/profile/{name}")

def updatePost(request, post_id):
    updatedPost = request.body.decode('utf-8') # decode the body to just the string the user wants to update the post to

    try:
        post = Post.objects.get(pk=int(post_id))

        # check if the user is the owner of the post
        if request.user.username != post.owner:
            return HttpResponse(500)

        post.text = updatedPost
        post.save()
        return HttpResponse(200)
    except:
        return HttpResponse(500)