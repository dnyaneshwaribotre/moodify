import api from './api'

export async function getFavorites(limit = 100) {
  return (await api.get('/favorites/', { params: { limit } })).data
}

export async function addFavorite(songId) {
  return (await api.post('/favorites/', { song_id: songId })).data
}

export async function removeFavoriteBySong(songId) {
  return (await api.delete(`/favorites/by-song/${songId}/`)).data
}

export async function getListeningHistory(limit = 20) {
  return (await api.get('/history/', { params: { limit } })).data
}

export async function saveListeningHistory(payload) {
  return (await api.post('/history/', payload)).data
}

export async function getMoodHistory(limit = 20) {
  return (await api.get('/mood-history/', { params: { limit } })).data
}

export async function saveMoodAnalysis(payload) {
  return (await api.post('/mood-history/', payload)).data
}

export async function recordInteraction(songId, interactionType) {
  return (await api.post('/interactions/', {
    song_id: songId,
    interaction_type: interactionType,
  })).data
}

export async function getInteractions() {
  return (await api.get('/interactions/')).data
}

export async function updateProfile(payload) {
  return (await api.patch('/auth/profile/', payload)).data
}
