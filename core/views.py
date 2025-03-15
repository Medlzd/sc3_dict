from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, permissions
from .models import User, Word, ApprovalWorkflow, Contribution, PointsSystem
from .serializers import UserSerializer, WordSerializer, ApprovalWorkflowSerializer, ContributionSerializer, PointsSystemSerializer
from .utils import search_word_in_pdfs, generate_definition
import json

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

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
