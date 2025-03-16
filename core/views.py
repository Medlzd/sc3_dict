from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, permissions
from .models import User, Word, ApprovalWorkflow, Contribution, PointsSystem
from .serializers import UserSerializer, WordSerializer, ApprovalWorkflowSerializer, ContributionSerializer, PointsSystemSerializer
from .utils import search_word_in_pdfs, generate_definition
import json
from core.models import WordHistory  # Assure-toi que le modèle est bien importé

from rest_framework.decorators import action
from rest_framework.response import Response



class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
class IsModeratorOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['moderator', 'admin']


class WordViewSet(viewsets.ModelViewSet):
    queryset = Word.objects.all()
    serializer_class = WordSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'], permission_classes=[IsModeratorOrAdmin])
    def change_status(self, request, pk=None):
        """Permet aux modérateurs de changer le statut d'un mot."""
        word = self.get_object()
        new_status = request.data.get('status')
        comment = request.data.get('comment', '')
        
        if new_status not in ['review', 'approved']:
            return Response({'error': 'Statut invalide'}, status=400)
        
        # Enregistrer l'historique
        WordHistory.objects.create(
            word=word,
            previous_status=word.status,
            new_status=new_status,
            changed_by=request.user,
            comment=comment
        )
        
        # Mettre à jour le mot
        word.status = new_status
        word.moderator_comment = comment
        word.save()
        return Response({'message': f'Statut mis à jour en {new_status}'})
    
    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def history(self, request, pk=None):
        """Récupère l'historique des changements de statut d'un mot."""
        word = self.get_object()
        history = word.history.all().values('previous_status', 'new_status', 'changed_by__username', 'changed_at', 'comment')
        return Response(list(history))


class ApprovalWorkflowViewSet(viewsets.ModelViewSet):
    queryset = ApprovalWorkflow.objects.all()
    serializer_class = ApprovalWorkflowSerializer
    permission_classes = [permissions.IsAuthenticated]


class ContributionViewSet(viewsets.ModelViewSet):
    queryset = Contribution.objects.all()
    serializer_class = ContributionSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'], permission_classes=[IsModeratorOrAdmin])
    def add_comment(self, request, pk=None):
        contribution = self.get_object()
        comment = request.data.get('comment', '').strip()
        if not comment:
            return Response({'error': 'Comment cannot be empty'}, status=400)
        contribution.comment = comment
        contribution.save()
        return Response({'message': 'Comment added successfully'})


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
