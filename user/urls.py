from django.urls import path

import user
import user.views

urlpatterns = [
    path("Register/",view=user.views.Register), 
    path("Login/",view=user.views.Login),
    path("get-user-data/",view=user.views.get_user_information),
    path("save-user-answers/", view= user.views.save_user_answers),
    path('GetEvaluation/', view=user.views.get_student_evaluation), 
    path('StoreEvaluation/', view=user.views.store_evaluation),
    path('translate-pdf/', view=user.views.translate_pdf_view, name='translate_pdf'),

]