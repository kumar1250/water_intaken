from django.urls import path
from .views import WaterIntakeView

urlpatterns = [
    path(
        'water-intake/',
        WaterIntakeView.as_view({'post': 'post'}),
        name='water-intake'
    ),
]