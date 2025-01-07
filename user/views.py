import json
import os
import uuid
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from user.serializer import UserSerializer
from .models import user
from django.utils.timezone import now
import requests

# Create your views here.
@api_view(['POST'])
def Register(request): 
    # check if the user already exists
    usr = user.objects.filter(email=request.data["email"])
    if usr: 
        return Response({'success':False, "message": "This email already exists!"})
    
    image = request.FILES.get('img')
    if not image:
        return Response({"success": False, 'message':'no image was uploaded'})
    ext = image.name.split('.')[-1]
    new_filename = f"{uuid.uuid4().hex}{now().strftime('%Y%m%d_%H%M%S')}.{ext}"
    image.name = new_filename
    request.data['img'] = image
   
    # create the user serializer
    user_serializer = UserSerializer(data=request.data) # create the serializer to convert the complex data into python compatible data to be able to set it in json format
    
    # check the serializer created and commit to the data base (to the user model)
    if user_serializer.is_valid():
        user_serializer.save()
        return Response({'success':True, "message": "Logged in successfully"})
    else : 
        return Response({"success":False, "message": "Something happened"})


@api_view(['POST'])
def Login(request): 
    # check if the user exists in the data base
    try: 
        usr = user.objects.filter(email = request.data['email']).first()
        if not usr: 
            return Response({"seccess":False, "message": "wrong credentials"})
        if not usr.check_password(request.data['password']):
            return Response({"seccess":False, "message": "wrong credentials"})
        elif usr and usr.check_password(request.data['password']): # repeat the check just in case we miss some case where it can bypass this if statements. 
            return Response({"success": True,"message":"logged in successfully"})
    except user.DoesNotExist: 
        return Response({"success": False, "Message":"Wrong credentials"})
    

@api_view(['POST'])
def get_user_information(request): 
 # check if the user exists in the data base
    try: 
        usr = user.objects.filter(email = request.data['email']).first()
        print(request)
        if not usr: 
            return Response({"success":False,'message':'no user with this email', "data":""})
        
        else : 
            data = {
                "image" : usr.img.url, # you guys can change in here if you want to retreive other data.
                }
            print(usr.img)
            return Response({'success': True,"message":"data loaded successfully", "data": data})
    except : 
        return Response({"success":False,'message':'Error happened',"data":""})


@api_view(['POST'])
def save_user_answers(request): 
    user_email = request.data['email']
    user_answers = request.data['answers']
    
    # Check if the user exists
    usr = user.objects.filter(email=user_email).first()
    if not usr:
        return Response({"success": False, "message": "User does not exist"})
    else:
        try:
            # Update the history of answers of the user
            usr.save_answers(user_answers)

            # Define the URL, headers, and prompt
            url = "http://localhost:5000/quiz-data/"
            headers = {
                "Content-Type": "application/json",
            }
            prompt = f'''
You are an assessment expert in Arabic-English-Arabic translation for students who are native
Darija speakers with Arabic as their first language and English as their second language. 
Analyze the student's performance in the exercise type below.
The evaluation you are going to give is going to be used to generate tailored exercises to resolve the weaknesses.

### Input Details:
All the answers of the student along with all the quizzes the student took: {user_answers}

### Task:
2. Summarize the overall performance:
   - Accuracy percentage.
   - Common error patterns.
   - Strengths and weaknesses specific to the exercise type.
3. Provide tailored recommendations for improvement:
   - Suggest strategies or resources for practice.
   - Recommend the next level of exercises based on performance.

### Output Format:
dont add any thing extra excpet exactly this structure without ````
{{
  "accuracy": "<accuracy percentage>",
  "overall_summary": {{
    "strengths": ["<list of strengths>"],
    "weaknesses": ["<list of weaknesses>"],
    "recommendations": ["<specific suggestions for improvement>"]
  }}, 
    "perfomance" : "an overall perofmance of the student, weak, advanced, what he lacks in concise words"

}}
'''
            # Send the prompt to the model for evaluation
            payload = {"prompt": prompt}
            response = requests.post(url=url, json=payload, headers=headers) 
            
            # if the user have no previous evaluations on performance then save he response of the above request
            if usr.evaluation is None : 
                usr.evaluation = response.json()
                usr.save()

            # if there is some eveluation then we can merge them into one with trakcing if the user has been progressin or not.
            else :
                prompt_eval = f'''
You are an assessment expert in Arabic-English-Arabic translation for students who are native
Darija speakers with Arabic as their first language and English as their second language. 
here are two evaluations of the student performance the old one {usr.evaluation} and the new evaluation {response}.
i would like you to summerize these two evaluations into one.
know that this evaluation is going to be used to generate exercices to the student, according to his level and perfomance.
follow exactly this structure 

the output of each field should summarize both performancess

### Output Format :
dont add any thing extra excpet excatly this structure without ````
{{
  "accuracy": "<accuracy percentage>",
  "overall_summary": {{
    "strengths": ["<list of strengths>"],
    "weaknesses": ["<list of weaknesses>"],
    "recommendations": ["<specific suggestions for improvement>"]
  }}, 
    "perfomance" : "an overall perofmance of the student, weak, advanced, what he lacks in concise words"

}}

'''             
                # sending the request to evelaute the student.
                payload = {"prompt": prompt_eval}
                eval = requests.post(url=url , json = payload, headers=headers)
                usr.evaluation = eval.json()
                usr.save()
            return Response({"success":True, "message" : "Answers saved successfully."})

        except Exception as e:
            print("Error:", str(e))
            return Response({"success": False, "message": "An error occurred."})

            
        except Exception as e : 
            return Response({"success":False, "message": "error happened"})
    


@api_view(['POST'])
def get_student_evaluation(request): 
    usr = user.objects.filter(email=request.data['email']).first()
    evaluation_data = json.loads(usr.evaluation)  # Convert string to dictionary
    perfomance = evaluation_data.get("perfomance", "")
    if not usr : 
        return Response({"success":False, "message": "USer does not exist"})
    else : 
        return Response({"success":True,"evaluation" : perfomance})
    


@api_view(['POST'])
def get_score(request): 
    email = request.data['email']
    usr = user.objects.filter(email=email).first()
    if not usr: 
        return Response({"success":False,"message": "user does not exits"})
    else : 
        evaluation_data = json.loads(usr.evaluation) 
        perfomance = evaluation_data.get("accuracy", "")
        return Response({"success":True, "score": perfomance})
    


@api_view(['POST'])
def get_number_corr_exos(request): 
    email = request.data['email']
    usr = user.objects.filter(email=email).first()
    if not usr: 
        return Response({"success":False,"message": "user does not exits"})
    else : 
        exos = json.loads(usr.evaluation) 
        return Response({"success":True, "score": len(exos)})
