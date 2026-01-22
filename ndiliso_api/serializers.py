from rest_framework import serializers
from .models import Funeral, Dependent, User , Village 


class VillageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Village
        fields = '__all__'


class FuneralSerializer(serializers.ModelSerializer):
    class Meta:
        model = Funeral
        fields = '__all__'
        read_only_fields = ['user']

class DependentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dependent
        fields = '__all__'
        read_only_fields = ['user']

class UserSerializer(serializers.ModelSerializer):
    village_id = serializers.PrimaryKeyRelatedField(
        queryset=Village.objects.all(),
        source='village'
    )

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'imageURL',
            'password',
            'village_id',
        ]
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)  # validated_data now contains `village`
        user.set_password(password)
        user.save()
        return user