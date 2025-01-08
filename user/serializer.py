from rest_framework import serializers
from .models import user

class UserSerializer(serializers.ModelSerializer): 
    class Meta(object): 
        model = user
        fields = ['id','username','email','img','password']
        extra_kwargs = {'password': {'write_only': True}}
        
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)

        #hash password
        if password is not None:
            instance.set_password(password)
            instance.save()
            return instance