from django.shortcuts import render, redirect, get_object_or_404
from .models import Profile, Meep
from django.contrib import messages 
from .forms import MeepForm, SignUpForm, ProfilePicForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User

def home(request):
    if request.user.is_authenticated:
        form = MeepForm(request.POST or None)
        if request.method == "POST":
            if form.is_valid():
                meep = form.save(commit=False)
                meep.user = request.user
                meep.save()
                messages.success(request, ("Your meep has been posted!"))
                return redirect('home')
        meeps = Meep.objects.all().order_by("-created_at")
        return render(request, 'home.html', {"meeps":meeps, "form":form})
    else:
        meeps = Meep.objects.all().order_by("-created_at")
        return render(request, 'home.html', {"meeps":meeps})

def profile_list(request):
    if request.user.is_authenticated:
        profiles = Profile.objects.exclude(user=request.user)
        return render(request, 'profile_list.html', {"profiles":profiles})
    else:
        messages.success(request, ("You Must be Logged in To")) 
        return redirect('home')

def unfollow(request, pk):
    if request.user.is_authenticated:
        #get profile unfollow
        profile = Profile.objects.get(user_id=pk)
        #unfollow user
        request.user.profile.follows.remove(profile)
        #save our profile
        request.user.profile.save()
        # return message
        messages.success(request, (f"you unfollowed {profile.user.username}"))
        return redirect(request.META.get("HTTP_REFERER"))

    else:
        messages.success(request, ("you must log in"))
        return redirect('home')
    
def follow(request, pk):
    if request.user.is_authenticated:
        #get profile unfollow
        profile = Profile.objects.get(user_id=pk)
        #unfollow user
        request.user.profile.follows.add(profile)
        #save our profile
        request.user.profile.save()
        # return message
        messages.success(request, (f"you followed {profile.user.username}"))
        return redirect(request.META.get("HTTP_REFERER"))

    else:
        messages.success(request, ("you must log in"))
        return redirect('home')



def profile(request, pk):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user_id=pk)
        meeps = Meep.objects.filter(user_id=pk).order_by("-created_at")

        #Post from logic
        if request.method == 'POST':
            # get current user ID
            current_user_profile = request.user.profile
            #get from data
            action = request.POST['follow']
            #decide to follow or unfollow
            if action == 'unfollow':
                current_user_profile.follows.remove(profile)
            elif action == 'follow':
                current_user_profile.follows.add(profile)
            #save the profile
            current_user_profile.save()

        return render(request, "profile.html", {"profile":profile, "meeps":meeps,})
    else:
        messages.success(request, ("You Must be Logged in To")) 
        return redirect('home')
    
def followers(request, pk):
    if request.user.is_authenticated:
        if request.user.id == pk:

            profiles = Profile.objects.get(user_id=pk)
            return render(request, 'followers.html', {"profiles":profiles})
        else:
            messages.success(request, ("Thats Not Your Profile")) 
            return redirect('home')
    else:
        messages.success(request, ("You Must be Logged in To")) 
        return redirect('home')
    
def follows(request, pk):
    if request.user.is_authenticated:
        if request.user.id == pk:

            profiles = Profile.objects.get(user_id=pk)
            return render(request, 'follows.html', {"profiles":profiles})
        else:
            messages.success(request, ("Thats Not Your Profile")) 
            return redirect('home')
    else:
        messages.success(request, ("You Must be Logged in To")) 
        return redirect('home')
    


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, ("You Logged in "))
            return redirect('home')
        else:
            messages.success(request, ("There was errro Logging in "))
            return redirect('login')
    else:
        return render(request, "login.html", {})
    

def logout_user(request):
    logout(request)
    messages.success(request, ("You Logged Out "))
    return redirect('home')


def register_user(request):
    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            #first_name = form.cleaned_data['first_name']
            #second_name = form.cleaned_data['second_name']
            #email = form.cleaned_data['email']
            #log in user
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, ("You have registerd without error "))
            return redirect('home')
        
    return render(request, "register.html", {'form':form})


def update_user(request):
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        profile_user = Profile.objects.get(user__id=request.user.id)
        #get forms
        user_form = SignUpForm(request.POST or None,request.FILES or None, instance=current_user)
        profile_form = ProfilePicForm(request.POST or None, request.FILES or None, instance=profile_user)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            login(request, current_user)
            messages.success(request, ("you updated your profile"))
            return redirect('home')

        return render(request, "update_user.html", {'user_form':user_form, 'profile_form':profile_form})
    else:
        messages.success(request, ("you must log in"))
        return redirect('home')
    


def meep_like(request, pk):
    if request.user.is_authenticated:
        meep = get_object_or_404(Meep, id=pk)
        if meep.likes.filter(id=request.user.id):
            meep.likes.remove(request.user)
        else:
            meep.likes.add(request.user)
            messages.success(request, ("You have liked a post"))
        return redirect(request.META.get("HTTP_REFERER"))
    else:
        
        return redirect('home')


    
def meep_show(request, pk):
    meep = get_object_or_404(Meep, id=pk)
    if meep:
        return render(request, "meep_show.html", {'meep':meep})

    else:
        messages.success(request, ("Than Meep does not exist"))
        return redirect('home')
    


def delete_meep(request, pk):
     if request.user.is_authenticated:
        meep = get_object_or_404(Meep, id=pk)
        #check owner meep
        if request.user.username == meep.user.username:
             meep.delete()
             messages.success(request, ("you deleted a meep"))
             return redirect(request.META.get("HTTP_REFERER"))
        else:
             messages.success(request, ("not your meep"))
             return redirect('home')

     else:
         messages.success(request, ("Log In to delete Meep"))
         return redirect(request.META.get("HTTP_REFERER"))
     

def edit_meep(request,pk):
	if request.user.is_authenticated:
		# Grab The Meep!
		meep = get_object_or_404(Meep, id=pk)

		# Check to see if you own the meep
		if request.user.username == meep.user.username:
			
			form = MeepForm(request.POST or None, instance=meep)
			if request.method == "POST":
				if form.is_valid():
					meep = form.save(commit=False)
					meep.user = request.user
					meep.save()
					messages.success(request, ("Your Meep Has Been Updated!"))
					return redirect('home')
			else:
				return render(request, "edit_meep.html", {'form':form, 'meep':meep})
	
		else:
			messages.success(request, ("You Don't Own That Meep!!"))
			return redirect('home')

	else:
		messages.success(request, ("Please Log In To Continue..."))
		return redirect('home')
     

def search(request):
	if request.method == "POST":
		# Grab the form field input
		search = request.POST['search']
		# Search the database
		searched = Meep.objects.filter(body__contains = search)

		return render(request, 'search.html', {'search':search, 'searched':searched})
	else:
		return render(request, 'search.html', {})

def search_user(request):
	if request.method == "POST":
		# Grab the form field input
		search = request.POST['search']
		# Search the database
		searched = User.objects.filter(username__contains = search)

		return render(request, 'search_user.html', {'search':search, 'searched':searched})
	else:
		return render(request, 'search_user.html', {})
