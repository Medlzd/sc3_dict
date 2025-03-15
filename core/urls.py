from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, WordViewSet, ApprovalWorkflowViewSet, ContributionViewSet, PointsSystemViewSet, chatbot_query
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'words', WordViewSet)
router.register(r'approval', ApprovalWorkflowViewSet)
router.register(r'contributions', ContributionViewSet)
router.register(r'points', PointsSystemViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('chatbot/', chatbot_query, name='chatbot'),

]
