from django.urls import path

import user
import user.views

urlpatterns = [
    path("Register/",view=user.views.Register), 
    path("Login/",view=user.views.Login),
    path("get-user-data/",view=user.views.get_user_information),
    path("save-user-answers/", view= user.views.save_user_answers),
    path("print_data/",view=user.views.print_data), 
    path('GetEvaluation/', view=user.views.print_data), 
    path('test/', view= user.views.test)
]