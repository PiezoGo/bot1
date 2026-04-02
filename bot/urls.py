from django.urls import path
from .views import HomePageView, answer   # ← Fixed: import answer too

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('answer/', answer, name='answer'),   # ← Fixed
]