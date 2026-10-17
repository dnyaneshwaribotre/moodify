from django.contrib import admin
from django.http import JsonResponse
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from api import ai_views, views

def api_home(request):
    return JsonResponse({
        "service": "Moodify API (backend)",
        "message": "The backend is running. Open the app at http://localhost:5173",
        "health": "/api/health/",
        "admin": "/admin/",
    })


urlpatterns = [
    path("", api_home),
    path("admin/", admin.site.urls),
    path("api/health/", views.HealthView.as_view()),
    # auth
    path("api/auth/register/", views.RegisterView.as_view()),
    path("api/auth/login/", views.LoginView.as_view()),
    path("api/auth/refresh/", TokenRefreshView.as_view()),
    path("api/auth/profile/", views.ProfileView.as_view()),
    path("api/auth/logout/", views.LogoutView.as_view()),
    # AI tools
    path("api/ai/analyze-mood/", ai_views.MoodAnalyzeView.as_view()),
    path("api/ai/recommend/", ai_views.RecommendView.as_view()),
    path("api/ai/insights/", ai_views.InsightsView.as_view()),
    path("api/ai/rank-recommendations/", views.RecommendationRankView.as_view()),
    # catalog
    path("api/moods/", views.MoodListView.as_view()),
    path("api/songs/", views.SongListView.as_view()),
    path("api/songs/search/", views.SongSearchView.as_view()),
    path("api/songs/<int:pk>/", views.SongDetailView.as_view()),
    path("api/songs/<int:pk>/playback/", views.PlaybackView.as_view()),
    path("api/spotify/search/", views.SpotifySearchView.as_view()),
    path("api/trending/", views.TrendingView.as_view()),
    # user data
    path("api/playlists/", views.PlaylistListCreateView.as_view()),
    path("api/playlists/<int:pk>/", views.PlaylistDetailView.as_view()),
    path("api/favorites/", views.FavoriteListCreateView.as_view()),
    path("api/favorites/by-song/<int:song_id>/", views.FavoriteBySongView.as_view()),
    path("api/history/", views.HistoryListCreateView.as_view()),
    path("api/mood-history/", views.MoodHistoryListCreateView.as_view()),
    path("api/interactions/", views.InteractionListCreateView.as_view()),
]
