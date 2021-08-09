from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('wiki/<str:title>', views.entry, name='entry'),
    path('newentry', views.new_entry, name='newentry'),
    path('edit/<str:title>', views.edit_entry, name='editentry'),
    path('random', views.random_entry, name='random'),
]
