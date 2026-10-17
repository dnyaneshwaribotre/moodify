from django.contrib.auth import authenticate, get_user_model
from django.db.models import F, Q
from django.db.models.functions import Least
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import ListAPIView, RetrieveAPIView, ListCreateAPIView, RetrieveDestroyAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from .models import Profile, Song, Playlist, Favorite, ListeningHistory, MoodHistory, UserInteraction
from .serializers import UserSerializer, ProfileSerializer, RegisterSerializer, SongSerializer, PlaylistSerializer, FavoriteSerializer, HistorySerializer, MoodHistorySerializer, InteractionSerializer
from .recommendation_engine import INDIAN_LANGUAGES, MOOD_COMPAT, rank_recommendations
from .models import TRENDING_FROM_YEAR, CLASSIC_UNTIL_YEAR
User=get_user_model()
def auth_payload(user):
    refresh=RefreshToken.for_user(user)
    profile,_=Profile.objects.get_or_create(user=user)
    return {'access':str(refresh.access_token),'refresh':str(refresh),'user':UserSerializer(user).data,'profile':ProfileSerializer(profile).data}
class HealthView(APIView):
    permission_classes=[AllowAny]
    def get(self,request): return Response({'status':'ok','service':'moodify-django-api','database':'postgresql'})
class RegisterView(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        serializer=RegisterSerializer(data=request.data); serializer.is_valid(raise_exception=True)
        user=User.objects.create_user(username=serializer.validated_data['username'],email=serializer.validated_data['email'],password=serializer.validated_data['password'])
        Profile.objects.create(user=user)
        return Response(auth_payload(user),status=status.HTTP_201_CREATED)
class LoginView(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        email=request.data.get('email','').strip().lower(); password=request.data.get('password','')
        user=User.objects.filter(email__iexact=email).first()
        if not user or not user.check_password(password): return Response({'detail':'Invalid email or password.'},status=400)
        return Response(auth_payload(user))
class LogoutView(APIView):
    def post(self,request):
        try: RefreshToken(request.data.get('refresh','')).blacklist()
        except (TokenError,TypeError): pass
        return Response(status=204)
class ProfileView(APIView):
    def get(self,request):
        profile,_=Profile.objects.get_or_create(user=request.user)
        data=ProfileSerializer(profile).data; data['user']=UserSerializer(request.user).data
        return Response(data)
    def patch(self,request):
        profile,_=Profile.objects.get_or_create(user=request.user)
        serializer=ProfileSerializer(profile,data=request.data,partial=True); serializer.is_valid(raise_exception=True); serializer.save()
        data=serializer.data; data['user']=UserSerializer(request.user).data
        return Response(data)
class RecommendationRankView(APIView):
    def post(self,request):
        payload=request.data
        ranked=rank_recommendations(payload.get('candidates',[]),payload.get('mood','chill'),payload.get('energy_level','medium'),payload.get('profile'),payload.get('favorites'),payload.get('history'),payload.get('interactions'))
        return Response(ranked)
class MoodListView(APIView):
    permission_classes=[AllowAny]
    def get(self,request): return Response(['happy','sad','calm','energetic','romantic','angry','focused','party','sleepy','nostalgic','chill'])
class SongListView(ListAPIView):
    serializer_class=SongSerializer
    def get_queryset(self):
        qs=Song.objects.all(); mood=self.request.query_params.get('mood'); energy=self.request.query_params.get('energy_level')
        try: limit=min(int(self.request.query_params.get('limit',50)),100)
        except (TypeError, ValueError): limit=50
        if mood:
            qs=qs.filter(mood__in=MOOD_COMPAT.get(mood,[mood,'chill']))
        if energy:
            energy_qs = Q(energy_level=energy)
            if mood:
                energy_qs |= Q(mood=mood)
            qs = qs.filter(energy_qs)
        return qs.order_by('-popularity_score','title')[:limit]
class SongSearchView(ListAPIView):
    serializer_class=SongSerializer; permission_classes=[AllowAny]
    def get_queryset(self):
        q=self.request.query_params.get('q','').strip()
        if not q: return Song.objects.none()
        return Song.objects.filter(Q(title__icontains=q)|Q(artist__icontains=q)|Q(album__icontains=q)|Q(genre__icontains=q)).order_by('-popularity_score')[:30]
class SongDetailView(RetrieveAPIView): queryset=Song.objects.all(); serializer_class=SongSerializer; permission_classes=[AllowAny]
class PlaybackView(APIView):
    """What to play for a song: a YouTube video id (full song) and/or a 30-second preview. Looked up on first play."""
    throttle_classes=[ScopedRateThrottle]; throttle_scope='playback'
    def get(self,request,pk):
        from django.shortcuts import get_object_or_404
        from .playback import resolve_playback
        return Response(resolve_playback(get_object_or_404(Song,pk=pk)))
class PlaylistListCreateView(ListCreateAPIView):
    serializer_class=PlaylistSerializer
    def get_queryset(self): return Playlist.objects.filter(user=self.request.user).prefetch_related('playlist_songs__song')
class PlaylistDetailView(RetrieveDestroyAPIView):
    serializer_class=PlaylistSerializer
    def get_queryset(self): return Playlist.objects.filter(user=self.request.user).prefetch_related('playlist_songs__song')
class FavoriteListCreateView(ListCreateAPIView):
    serializer_class=FavoriteSerializer
    def get_queryset(self): return Favorite.objects.filter(user=self.request.user).select_related('song')
    def perform_create(self,serializer): serializer.save(user=self.request.user)
class FavoriteBySongView(APIView):
    def delete(self,request,song_id):
        Favorite.objects.filter(user=request.user,song_id=song_id).delete(); return Response(status=204)
class HistoryListCreateView(ListCreateAPIView):
    serializer_class=HistorySerializer
    def get_queryset(self):
        qs=ListeningHistory.objects.filter(user=self.request.user).select_related('song')
        try: limit=min(int(self.request.query_params.get('limit',20)),100)
        except ValueError: limit=20
        return qs[:limit]
    def perform_create(self,serializer): serializer.save(user=self.request.user)
class MoodHistoryListCreateView(ListCreateAPIView):
    serializer_class=MoodHistorySerializer
    def get_queryset(self):
        try: limit=min(int(self.request.query_params.get('limit',20)),100)
        except ValueError: limit=20
        return MoodHistory.objects.filter(user=self.request.user)[:limit]
    def perform_create(self,serializer): serializer.save(user=self.request.user)
class InteractionListCreateView(ListCreateAPIView):
    serializer_class=InteractionSerializer
    def get_queryset(self): return UserInteraction.objects.filter(user=self.request.user).select_related('song')[:100]
    def perform_create(self,serializer):
        interaction=serializer.save(user=self.request.user)
        if interaction.interaction_type=='play': Song.objects.filter(pk=interaction.song_id).update(plays=F('plays')+1)
class TrendingView(ListAPIView):
    """Songs by category. trending / classics show Indian songs; `global` shows English ones."""
    serializer_class=SongSerializer; permission_classes=[AllowAny]
    LANGUAGE_CATEGORIES={'hindi':['hindi'],'marathi':['marathi'],'english':['english'],'punjabi':['punjabi'],'south':['tamil','telugu']}
    def get_queryset(self):
        qs=Song.objects.all(); category=self.request.query_params.get('category','').lower() or 'trending'
        indian=Q(language__in=sorted(INDIAN_LANGUAGES))
        if category=='trending': qs=qs.filter(indian,release_year__gte=TRENDING_FROM_YEAR)
        elif category in ('classics','classic'): qs=qs.filter(indian,release_year__lte=CLASSIC_UNTIL_YEAR)
        elif category=='global': qs=qs.filter(language='english',release_year__gte=TRENDING_FROM_YEAR)
        elif category in self.LANGUAGE_CATEGORIES: qs=qs.filter(language__in=self.LANGUAGE_CATEGORIES[category])
        elif category in ('lo-fi','lofi'): qs=qs.filter(Q(genre__icontains='lo-fi')|Q(mood__in=['sleepy','calm']))
        try: limit=min(int(self.request.query_params.get('limit',20)),100)
        except ValueError: limit=20
        # popularity plus a small boost for songs people actually play inside Moodify
        return qs.annotate(trend_score=F('popularity_score')+Least(F('plays'),20)).order_by('-trend_score','title')[:limit]


class SpotifySearchView(APIView):
    """Search Spotify's catalog for metadata; full playback remains on YouTube."""
    permission_classes = [AllowAny]

    def get(self, request):
        from .spotify import search_tracks, spotify_enabled
        query = request.query_params.get("q", "").strip()
        if not query:
            return Response({"detail": "Provide a search query using ?q=."}, status=400)
        if not spotify_enabled():
            return Response({
                "detail": "Spotify integration is not configured. Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in backend/.env."
            }, status=503)
        try:
            tracks = search_tracks(query)
        except Exception:  # noqa: BLE001
            return Response({"detail": "Spotify search is temporarily unavailable."}, status=502)
        return Response({"results": tracks})
