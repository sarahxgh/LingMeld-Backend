from django.urls import path

import user
import user.views

urlpatterns = [
    path("Register/",view=user.views.Register), 
    path("Login/",view=user.views.Login),
    path("get-user-data/",view=user.views.get_user_information)
]