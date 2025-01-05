from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.shortcuts import redirect
from . import views

router = DefaultRouter()
router.register(r'forms', views.FormViewSet)
router.register(r'questions', views.QuestionViewSet)
router.register(r'responses', views.ResponseViewSet)

def redirect_to_login(request):
    return redirect('login')

urlpatterns = [
    path('api/', include(router.urls)),
    path('', redirect_to_login, name='home'),
    path('forms/', views.list, name='list'),
    path('form/<int:form_id>/', views.fview, name='fview'),
    path('form/<int:form_id>/analytics/', views.analytics, name='analytics'),
    path('form/<int:form_id>/submit/', views.fsubmit, name='fsubmit'),
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', views.user_logout, name='logout'),
]
