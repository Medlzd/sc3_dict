from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, WordViewSet, ApprovalWorkflowViewSet, ContributionViewSet, PointsSystemViewSet, chatbot_query,LoginView,RegisterUserView
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'words', WordViewSet)
router.register(r'approval', ApprovalWorkflowViewSet)
router.register(r'contributions', ContributionViewSet)
router.register(r'points', PointsSystemViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api/auth/login/', LoginView.as_view(), name='login_users'),
    path('api/auth/register/', RegisterUserView.as_view(), name='register_users'),
    path('chatbot/', chatbot_query, name='chatbot'),

]
