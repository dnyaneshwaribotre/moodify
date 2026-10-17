import api from './api'

// AI tool 1: read a mood (words, emoji, Hindi/Marathi...) -> mood, energy, language, era
export async function analyzeMood(text) { return (await api.post('/ai/analyze-mood/', { text })).data }

// AI tool 2: ranked session split into trending hits / famous classics / more, with a reason per song
export async function getRecommendations(payload) { return (await api.post('/ai/recommend/', payload)).data }

// AI tool 3: personal mood insight + time-of-day suggestion
export async function getInsights() { return (await api.get('/ai/insights/')).data }

export async function rankRecommendations(payload) { return (await api.post('/ai/rank-recommendations/', payload)).data }
