import io
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
from pdfminer.high_level import extract_text
from transformers import MarianMTModel, MarianTokenizer
from datetime import datetime, timedelta
import threading
import time
from datetime import datetime, timedelta
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import user
from django.utils import timezone
import logging

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

            return Response({"success": True,"message":"logged in successfully","taken_test" : usr.hasTakentest})
        
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

    try:
        # Update the history of answers of the user
        usr.save_answers(user_answers)

        # Define the URL, headers, and prompt
        url = "http://127.0.0.1:8000//quiz-data/"
        headers = {
            "Content-Type": "application/json",
        }
        prompt = f'''
        You are an assessment expert in Arabic-English-Arabic translation.
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

        # Ensure the response contains valid JSON data
        if response.status_code == 200:
            evaluation_data = response.json()
            usr.evaluation = json.dumps(evaluation_data)  # Convert dictionary to JSON string
            usr.save()
            return Response({"success": True, "message": "Answers saved successfully."})
        else:
            return Response({"success": False, "message": "Failed to evaluate answers"})
    except Exception as e:
        print("Error:", str(e))
        return Response({"success": False, "message": "An error occurred."})
    
@api_view(['POST'])
def get_student_evaluation(request):
    try:
        usr = user.objects.filter(email=request.data['email']).first()
        if not usr:
            return Response({"success": False, "message": "User does not exist"})

        # Check if evaluation is empty or invalid
        if not usr.evaluation:
            return Response({"success": False, "message": "No evaluation data found"})

        try:
            evaluation_data = json.loads(usr.evaluation)  # Convert string to dictionary
            performance = evaluation_data.get("perfomance", "")
            return Response({"success": True, "evaluation": performance})
        except json.JSONDecodeError:
            return Response({"success": False, "message": "Invalid evaluation data"})
    except Exception as e:
        return Response({"success": False, "message": str(e)})
    

@api_view(['POST'])
def get_score(request):
    email = request.data['email']
    usr = user.objects.filter(email=email).first()
    if not usr:
        return Response({"success": False, "message": "User does not exist"})

    try:
        if not usr.evaluation:
            return Response({"success": False, "message": "No score data found"})

        evaluation_data = json.loads(usr.evaluation)
        performance = evaluation_data.get("accuracy", "")
        return Response({"success": True, "score": performance})
    except json.JSONDecodeError:
        return Response({"success": False, "message": "Invalid score data"})
    except Exception as e:
        return Response({"success": False, "message": str(e)})


@api_view(['POST'])
def get_number_corr_exos(request):
    email = request.data['email']
    usr = user.objects.filter(email=email).first()
    if not usr:
        return Response({"success": False, "message": "User does not exist"})

    try:
        # Check if evaluation is empty or invalid
        if not usr.evaluation:
            return Response({"success": False, "message": "No number_corr_exos data found"})

        # Parse the evaluation data
        exos = json.loads(usr.evaluation)
        return Response({"success": True, "score": len(exos)})
    except json.JSONDecodeError:
        return Response({"success": False, "message": "Invalid evaluation data"})
    except Exception as e:
        return Response({"success": False, "message": str(e)})

# 1. Load MarianMT for Arabic->English
ar_en_model_name = "Helsinki-NLP/opus-mt-ar-en"
ar_en_tokenizer = MarianTokenizer.from_pretrained(ar_en_model_name)
ar_en_model = MarianMTModel.from_pretrained(ar_en_model_name)

# 2. Load MarianMT for English->Arabic
en_ar_model_name = "Helsinki-NLP/opus-mt-en-ar"
en_ar_tokenizer = MarianTokenizer.from_pretrained(en_ar_model_name)
en_ar_model = MarianMTModel.from_pretrained(en_ar_model_name)

@api_view(['POST'])
def translate_pdf_view(request):
    print("hello")
    """
    Receives a PDF, extracts text with pdfminer, translates it using MarianMT.
    Expects the form field "file" for the uploaded PDF.
    Also optionally "direction": 'ar-en' or 'en-ar'.
    """
    pdf_file = request.FILES.get('file')
    print(pdf_file)
    # For example, default to Arabic->English if not specified
    direction = request.data['direction']
    print(direction)

    if not pdf_file:
        return Response({"success":True,"message": "No PDF file provided."})

    try:
        # Extract the text from the PDF
        extracted_text = extract_text_from_pdf(pdf_file)
        print(extract_text)

        # Translate based on direction
        if direction == 'ar-en':
            translated_text = translate_ar_to_en(extracted_text)
        elif direction == 'en-ar':
            translated_text = translate_en_to_ar(extracted_text)
        else:
            return Response({"success":False,"message": "Invalid translation direction."})
        print("here",translated_text)
        return Response({
            "success" : True,
            "message": "uploaded successfully",
            "extracted_text": extracted_text,
            "translated_text": translated_text
        })

    except Exception as e:
        return Response(
            {"success":False,
                "message": str(e)}, 
        )


def extract_text_from_pdf(pdf_file):
    """
    Extracts text from a PDF using pdfminer.six.
    """
    pdf_data = pdf_file.read()
    pdf_file.seek(0)  # reset pointer if needed later
    text = extract_text(io.BytesIO(pdf_data))
    return text.strip()


def translate_ar_to_en(text: str) -> str:
    """
    Translate Arabic -> English using MarianMT
    """
    # Tokenize
    inputs = ar_en_tokenizer([text], return_tensors="pt", padding=True, truncation=True)
    # Generate translation
    translated_tokens = ar_en_model.generate(**inputs)
    # Decode to string
    translation = ar_en_tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)
    return translation[0]


def translate_en_to_ar(text: str) -> str:
    """
    Translate English -> Arabic using MarianMT
    """
    # Tokenize
    inputs = en_ar_tokenizer([text], return_tensors="pt", padding=True, truncation=True)
    # Generate translation
    translated_tokens = en_ar_model.generate(**inputs)
    # Decode to string
    translation = en_ar_tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)
    return translation[0]





logger = logging.getLogger(__name__)

@api_view(['POST'])
def update_active_hours(request):
    email = request.data['email']
    usr = user.objects.filter(email=email).first()
    if not usr:
        return Response({"success": False, "message": "User does not exist"})

    now = timezone.now()
    last_active = usr.last_active

    # Ensure last_active is timezone-aware
    if last_active and timezone.is_naive(last_active):
        last_active = timezone.make_aware(last_active)

    # Calculate the time difference in hours
    time_difference = now - last_active
    hours_difference = time_difference.total_seconds() / 3600  # Convert seconds to hours

    # Update active hours if the time difference is at least 1 hour
    if hours_difference >= 1:
        usr.active_hours += hours_difference  # Add the difference in hours
        usr.last_active = now  # Update the last active time
        usr.save()
        logger.info(f"Updated active hours for user {email}. Added {hours_difference:.2f} hours.")
        return Response({"success": True, "message": "Active hours updated successfully"})
    else:
        logger.debug(f"No update needed for user {email}. Time difference: {hours_difference:.2f} hours.")
        return Response({"success": True, "message": "No update needed (less than 1 hour)"})


@api_view(['POST'])
def get_active_days(request):
    email = request.data['email']
    usr = user.objects.filter(email=email).first()
    if not usr:
        return Response({"success": False, "message": "User does not exist"})

    # Convert active hours to days (assuming 8 hours per day)
    HOURS_PER_DAY = 24
    active_days = usr.active_hours / HOURS_PER_DAY

    # Round to 1 decimal place for better readability
    active_days_rounded = round(active_days, 1)

    return Response({"success": True, "active_days": active_days_rounded})

@api_view(['POST'])
def get_average_score(request):
    email = request.data['email']
    usr = user.objects.filter(email=email).first()
    if not usr:
        return Response({"success": False, "message": "User does not exist"})

    try:
        if not usr.evaluation:
            return Response({"success": False, "message": "No evaluation data found"})

        # Parse the evaluation data
        evaluation_data = json.loads(usr.evaluation)

        # Check if the evaluation data is a list of evaluations
        if isinstance(evaluation_data, list):
            # Calculate the average score
            total_score = 0
            count = 0
            for evaluation in evaluation_data:
                if isinstance(evaluation, dict) and "accuracy" in evaluation:
                    total_score += float(evaluation["accuracy"])
                    count += 1

            if count > 0:
                average_score = total_score / count
            else:
                average_score = 0  # No valid scores found
        else:
            # Handle single evaluation (legacy format)
            if "accuracy" in evaluation_data:
                average_score = float(evaluation_data["accuracy"])
            else:
                average_score = 0  # No valid score found

        return Response({"success": True, "average_score": average_score})
    except json.JSONDecodeError:
        return Response({"success": False, "message": "Invalid evaluation data"})
    except Exception as e:
        return Response({"success": False, "message": str(e)})