import api from './api'
export async function getUserPlaylists() { return (await api.get('/playlists/')).data }
export async function getPlaylistById(id) { return (await api.get(`/playlists/${id}/`)).data }
export async function createPlaylist(payload) { return (await api.post('/playlists/', { ...payload, song_ids: (payload.songs || []).map(song => song.id) })).data }
export async function deletePlaylist(id) { return (await api.delete(`/playlists/${id}/`)).data }
