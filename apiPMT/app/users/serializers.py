from rest_framework import serializers
from .models import User
from app.projects.models import Project
from app.tasks.models import Task
from rest_framework.exceptions import ValidationError as DRFValidationError


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name']


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title']


class UserSerializer(serializers.ModelSerializer):
    projects = ProjectSerializer(many=True, read_only=True)
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'position', 'projects', 'tasks', 'created_at']
        read_only_fields = ['created_at']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
        )
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    projects = serializers.PrimaryKeyRelatedField(many=True, queryset=Project.objects.all(), required=False)
    tasks = serializers.PrimaryKeyRelatedField(many=True, queryset=Task.objects.all(), required=False)
    position = serializers.ChoiceField(choices=User.POSITION_CHOICES, required=False)

    class Meta:
        model = User
        fields = ['username', 'password', 'position', 'projects', 'tasks']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
        }

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            instance.set_password(validated_data.pop('password'))
        try:
            return super().update(instance, validated_data)
        except DRFValidationError as e:
            raise serializers.ValidationError(e.detail)
