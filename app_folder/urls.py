from django.urls import path
from . import views
from app_folder.models import AudioFile
from django.conf import settings
from django.conf.urls.static import static
from .listening import practiceview
from . import listening
from .listening import check_audio_file

from .views import entryview, loginview, logoutview, record_view, select_page_view

app_name = 'app_folder'

urlpatterns = [
    path('entry/', entryview, name='entry'),
    path('login/', loginview, name='login'),
    path('logout/', logoutview, name='logout'),
    path('listening/', practiceview, name='listening'),
    path('check-audio/<int:page>/<int:question>/<str:person>/',check_audio_file, name='check-audio-file'),
    path('check-audio/<int:page>/<int:question>/<str:person>/<str:pattern>/',check_audio_file, name='check-audio-file-pattern'),
    path('top_page/', views.top_page, name='top_page'),
    path('select_page/', views.select_page_view, name='select_page'),
    path('record_view/', record_view, name='record_view'),
    path("plot_pitch/", views.plot_pitch_view, name="plot_pitch"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


