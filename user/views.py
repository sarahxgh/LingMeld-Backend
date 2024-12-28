from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from user.serializer import UserSerializer
from .models import user
# Create your views here.
@api_view(['POST'])
def Register(request): 
    # check if the user already exists
    usr = user.objects.filter(email=request.data["email"])
    if usr: 
        return Response({'success':False, "message": "This email already exists!"})

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
def set_user_information(request): 
    pass