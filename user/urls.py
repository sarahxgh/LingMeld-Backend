from django.urls import path
from . import views 
import user
import user.views

urlpatterns = [
    path("Register/",view=user.views.Register), 
    path("Login/",view=user.views.Login),
    path("get-user-data/",view=user.views.get_user_information),
    path("save-user-answers/", view= user.views.save_user_answers),
    path('GetEvaluation/', views.get_student_evaluation, name='get_student_evaluation'), 
     path('GetScore/', user.views.get_score, name='get_score'),
    path('get_number_corr_exos/', user.views.get_number_corr_exos, name='get_number_corr_exos'),
    path('translate-pdf/', view=user.views.translate_pdf_view, name='translate_pdf'),
    path('get_active_days/', user.views.get_active_days, name='get_active_days'),
    path('get_average_score/', user.views.get_average_score, name='get_average_score'),
    path('update_active_hours/', user.views.update_active_hours, name='update_active_hours'),
]