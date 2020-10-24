from django.urls import path
from . import views

urlpatterns = [
    path('index/', views.index, name='index'),
    path("", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("meals/", views.meals, name="meals"),
    path("create_meal/", views.create_meal, name="create_meal"),
    path("goal_change/", views.goal_change, name="goal_change"),
    path("add_food/", views.add_food, name="add_food"),
    path("goal_change/", views.cal_calc, name="cal_calc"),
    path("search_meal/", views.search_meal, name="search_meal"),
    path('delete/<int:food_id>', views.delete, name='delete'),
    path("upload_workout/", views.showvideo, name="upload_workout"),
    path('all_workout/', views.display, name='all_workout'),
    path('recipe_upload/', views.recipe_upload, name='recipe_upload'),
    path('display_recipe/', views.recipe_display, name='display_recipe'),
]
