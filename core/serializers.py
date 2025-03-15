from rest_framework import serializers
from .models import User, Word, ApprovalWorkflow, Contribution, PointsSystem

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']

class WordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Word
        fields = '__all__'

class ApprovalWorkflowSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApprovalWorkflow
        fields = '__all__'

class ContributionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contribution
        fields = '__all__'

class PointsSystemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PointsSystem
        fields = '__all__'
