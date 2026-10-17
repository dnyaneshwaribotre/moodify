import api from './api'
export async function searchSongs(query) { if (!query?.trim()) return []; return (await api.get('/songs/search/', { params: { q: query } })).data }
export async function getCandidateSongs(mood, energyLevel, limit = 50) { return (await api.get('/songs/', { params: { mood, energy_level: energyLevel, limit } })).data }
export async function getSongById(id) { return (await api.get(`/songs/${id}/`)).data }
export async function getTrendingSongs(category = null, limit = 20) { return (await api.get('/trending/', { params: { category: category || '', limit } })).data }

// Spotify Web API search returns track metadata/links only; full playback is handled by YouTube.
export async function searchSpotifyTracks(query) {
  if (!query?.trim()) return []
  const { data } = await api.get('/spotify/search/', { params: { q: query } })
  return data.results || []
}
