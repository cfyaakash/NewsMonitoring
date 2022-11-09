from django.urls import include, re_path, path
# from core import views as core_views

from . import views

app_name = 'newsStories'
urlpatterns = [
    path('', views.index, name='index'),
    path('source', views.source, name='source'),
    path('sources', views.sourceList, name='sources'),
    path('update/<int:pk>', views.update_source, name='update'),
    path('delete/<int:pk>', views.source_delete, name='delete'),
    path('updatestory/<int:pk>', views.update_story, name='updatestory'),
    path('storydelete/<int:pk>', views.story_delete, name='storydelete'),
    path('search', views.source_search, name='search'),
    path('storyadd', views.add_story, name='storyadd'),
    path('storylist', views.story_listing, name='storylist'),
    path('storysearch', views.story_search, name='storysearch'),
    path('fetch/<int:pk>', views.story_fetch, name='fetch'),

]
