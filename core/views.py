from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, permissions
from .models import User, Word, ApprovalWorkflow, Contribution, PointsSystem
from .serializers import UserSerializer, WordSerializer, ApprovalWorkflowSerializer, ContributionSerializer, PointsSystemSerializer
from .utils import search_word_in_pdfs, generate_definition
import json
from rest_framework import status
from rest_framework.views import APIView

from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType  # ✅ Import this!

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({
                'error': 'Username and password are required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        print(f"Received credentials: username={username}, password={password}")

        user = authenticate(username=username, password=password)
        
        if user is not None:
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token

            return Response({

                'refresh': str(refresh),
                'access': str(access_token),
                'id':user.id,
                'username': user.username,
                'role': user.role,
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Invalid credentials'
                
            }, status=status.HTTP_401_UNAUTHORIZED)
class RegisterUserView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            # Ensure groups exist
            admin_group, _ = Group.objects.get_or_create(name='Admin')
            moderator_group, _ = Group.objects.get_or_create(name='Moderator')
            contributor_group, _ = Group.objects.get_or_create(name='Contributor')

            # Ensure permissions exist with correct content type
            user_content_type = ContentType.objects.get_for_model(User)
            
            permission_view_users, _ = Permission.objects.get_or_create(
                codename='can_view_users',
                name='Can view users',
                content_type=user_content_type
            )
            permission_edit_users, _ = Permission.objects.get_or_create(
                codename='can_edit_users',
                name='Can edit users',
                content_type=user_content_type
            )

            # Assign permissions to groups
            admin_group.permissions.add(permission_view_users, permission_edit_users)
            moderator_group.permissions.add(permission_view_users)
            contributor_group.permissions.add(permission_view_users)

            # Register user
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                user.set_password(serializer.validated_data["password"])
                user.save()

                # Assign user to role-based group
                role = user.role.lower()
                if role == 'admin':
                    user.groups.add(admin_group)
                elif role == 'moderator':
                    user.groups.add(moderator_group)
                elif role == 'contributor':
                    user.groups.add(contributor_group)

                return Response({
                    "message": "User created and groups, permissions assigned successfully"
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "error": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class WordViewSet(viewsets.ModelViewSet):
    queryset = Word.objects.all()
    serializer_class = WordSerializer
    permission_classes = [permissions.IsAuthenticated]

class ApprovalWorkflowViewSet(viewsets.ModelViewSet):
    queryset = ApprovalWorkflow.objects.all()
    serializer_class = ApprovalWorkflowSerializer
    permission_classes = [permissions.IsAuthenticated]

class ContributionViewSet(viewsets.ModelViewSet):
    queryset = Contribution.objects.all()
    serializer_class = ContributionSerializer
    permission_classes = [permissions.IsAuthenticated]

class PointsSystemViewSet(viewsets.ModelViewSet):
    queryset = PointsSystem.objects.all()
    serializer_class = PointsSystemSerializer
    permission_classes = [permissions.IsAuthenticated]

@csrf_exempt
def chatbot_query(request):
    """
    Handles natural language queries about Hassaniya words.
    - **First**, searches for the word in PDFs.
    - **If not found**, asks Groq AI to generate a definition.
    - **If AI also doesn't know**, asks the user to provide a definition.
    """
    if request.method == "POST":
        data = json.loads(request.body)
        user_input = data.get("query", "").strip()

        if not user_input:
            return JsonResponse({"error": "Aucune requête fournie"}, status=400)

        # ✅ Search in PDFs first
        pdf_result = search_word_in_pdfs(user_input)
        if pdf_result:
            return JsonResponse(pdf_result)

        # ✅ If not found, ask AI for a definition in **French**
        ai_response = generate_definition(user_input)

        if "Je ne connais pas ce mot" in ai_response:
            return JsonResponse({
                "response": f"Je ne connais pas ce mot. Pouvez-vous m'expliquer '{user_input}' ? J'apprendrai de votre réponse."
            })

        return JsonResponse({"word": user_input, "definition": ai_response})

    return JsonResponse({"error": "Requête invalide"}, status=400)
