from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Meal, Profile
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.db.models import Sum
import requests
from django.utils import timezone


def base(request):
    context = {
        "user": request.user,
    }
    return render(request, "tracker/base.html", context)


def index(request):
    profile = Profile.objects.get(user=request.user)
    date_now = timezone.now().date()
    kcal = Meal.objects.filter(date=date_now, userfk=request.user).aggregate(Sum('kcal'))['kcal__sum'] or 0.00
    goal_cals = profile.goal_cals
    if kcal is not None:
        kcal_total = int(kcal)
        kcal_left = goal_cals - kcal_total
    else:
        kcal_total = 0
        kcal_left = goal_cals
    if not request.user.is_authenticated:
        return render(request, "tracker/login.html", {"message": None})
    progress = (int(kcal) / int(goal_cals)) * 100
    context = {
        "user": request.user,
        "date": timezone.now().date(),
        "kcal_total": int(kcal_total),
        "kcal_left": int(kcal_left),
        "kcal_goal": int(goal_cals),
        "progress": int(progress)
    }
    return render(request, "tracker/index.html", context)


def register(request):
    if request.method == 'POST':
        try:
            user = User.objects.create_user(username=request.POST["username"],
                                            email=request.POST["email"],
                                            password=request.POST["password"])
            user.save()
            profile = Profile.objects.create(
                goal_cals=2000,
                user=user)
            profile.save()
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        except:
            return error(request, 'You must fill in all info')
    elif request.method == 'GET':
        return render(request, "tracker/register.html")


def login_view(request):
    if request.method == 'POST':
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "tracker/login.html", {"message": "Invalid credentials."})
    elif request.method == 'GET':
        return render(request, "tracker/login.html")


def logout_view(request):
    logout(request)
    return render(request, "tracker/login.html", {"message": "Logged out."})


def meals(request):
    user = request.user
    meals = Meal.objects.filter(userfk=user).order_by('date')
    if request.method == "POST":
        search = request.POST.get("searchbox", False)
        search_but = request.POST.get("search")
        if search_but == "Search Your Recent Foods":
            meals = Meal.objects.filter(name__contains=search).filter(userfk=user)
            if not search or not meals:
                return redirect('search_meal')
        elif search_but == "Search Food From Other Entered":
            meals = Meal.objects.filter(name__contains=search)
            if not search or not meals:
                return redirect('search_meal')

    context = {
        'meals': meals,
        "user": request.user
    }
    return render(request, "tracker/meals.html", context)


def search_meal(request):
    if request.method == 'POST':
        try:
            name = request.POST["name"],
            quantity = request.POST["quantity"],
            name = str(name[0])
            name = name.replace(" ", "%20")
            quantity = quantity[0]
            url = 'https://api.edamam.com/api/nutrition-data?app_id=&ingr='+str(quantity)+'%20'+name
            response = requests.get(url)
            foodkcal = response.json()['calories']
            if foodkcal == 0:
                return redirect('create_meal')
            meal = Meal.objects.create(
                userfk=request.user,
                name=request.POST["name"],
                kcal=foodkcal,
                quantity=quantity,
                date=timezone.now().date()
            )
            meal.save()
            return redirect('index')
        except:
            return error(request, 'You left one or more fields blank.')
    elif request.method == 'GET':
        return render(request, 'tracker/search_meal.html')


def create_meal(request):
    if request.method == 'POST':
        try:
            meal = Meal.objects.create(
                userfk=request.user,
                name=request.POST["name"],
                kcal=request.POST["kcal"],
                quantity=request.POST["quantity"],
                date=timezone.now().date()
            )
            meal.save()
            return redirect('index')
        except:
            return error(request, 'You left one or more fields blank.')
    elif request.method == 'GET':
        context = {
            "user": request.user
        }
        return render(request, "tracker/create_meal.html", context)


def add_food(request):
    if request.method == 'POST':
        food_name = request.POST["food_name"]
        food_kcal = request.POST["food_kcal"]
        food_quantity = request.POST["food_quantity"]
        meal = Meal.objects.create(
            userfk=request.user,
            name=food_name,
            kcal=food_kcal,
            quantity=food_quantity,
            date=timezone.now().date())
        meal.save()
        return redirect('index')
    else:
        return render(request, "tracker/meals.html")


def cal_calc(request):
    if request.method == 'POST':
        gender = request.POST.get("gender")
        age = request.POST.get("age")
        lbs = request.POST.get("lbs")
        height = request.POST.get("height")
        activity = request.POST.get("activity")
        if gender is '1':
            bmr = 655 + (4.35 * int(lbs)) + \
                  (4.7 * int(height)) - (4.7 * int(age))
        elif gender is '0':
            bmr = 66 + (6.23 * int(lbs)) + \
                  (12.7 * int(height)) - (6.8 * int(age))
        daily = bmr * int(activity)
        weekly = daily * 7
    else:
        return render(request, "tracker/goal_change.html")
    context = {
        'daily': daily,
        'weekly': weekly,
        "user": request.user
    }
    return render(request, "tracker/goal_change.html", context)


def goal_change(request):
    if request.method == 'POST':
        timeframe = request.POST.get("timeframe", "0")
        goal = int(request.POST.get("goal", 2000))
        if timeframe is "1":
            goal = goal / 7
        Profile.objects.filter(user=request.user).update(goal_cals=goal)
        return HttpResponseRedirect(reverse("index"))
    else:
        context = {
            "user": request.user
        }
        return render(request, "tracker/goal_change.html", context)


def error(request, msg):
    context = {
        'msg': msg
    }
    return render(request, 'tracker/error.html', context)
