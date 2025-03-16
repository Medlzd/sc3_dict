from rest_framework import serializers
from .models import User, Word, ApprovalWorkflow, Contribution, PointsSystem

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'role','email']
    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data["username"],
            email=validated_data["email"],
            role=validated_data.get("role", "contributor")
        )
        user.set_password(validated_data["password"])
        user.save()
        return user
class WordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Word
        fields = ['id', 'text', 'definition', 'status', 'created_at', 'moderator_comment']
        read_only_fields = ['status', 'created_at', 'created_by']  # Ensure `created_by` is not required in input

    def create(self, validated_data):
        request = self.context.get('request')  # Get request context
        if request and request.user.is_authenticated:
            validated_data['created_by'] = request.user
        return super().create(validated_data)
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
