export const MOOD_CONFIG = {
  happy: { icon: '😊', label: 'Happy', color: '#FFD93D', gradient: 'linear-gradient(135deg, #FFD93D, #FF9F2D)' },
  sad: { icon: '😢', label: 'Sad', color: '#4A90D9', gradient: 'linear-gradient(135deg, #4A90D9, #2C5F8A)' },
  calm: { icon: '😌', label: 'Calm', color: '#66D9A8', gradient: 'linear-gradient(135deg, #66D9A8, #3AB98A)' },
  energetic: { icon: '⚡', label: 'Energetic', color: '#FF6B6B', gradient: 'linear-gradient(135deg, #FF6B6B, #EE3838)' },
  romantic: { icon: '❤️', label: 'Romantic', color: '#FF8AB8', gradient: 'linear-gradient(135deg, #FF8AB8, #E63992)' },
  party: { icon: '🎉', label: 'Party', color: '#FF00FF', gradient: 'linear-gradient(135deg, #FF00FF, #8A2BE2)' },
  sleepy: { icon: '😴', label: 'Sleepy', color: '#6C7B95', gradient: 'linear-gradient(135deg, #6C7B95, #3E4C68)' },
  focused: { icon: '🎯', label: 'Focused', color: '#5DADE2', gradient: 'linear-gradient(135deg, #5DADE2, #2980B9)' },
  nostalgic: { icon: '📼', label: 'Nostalgic', color: '#D4A574', gradient: 'linear-gradient(135deg, #D4A574, #A0764E)' },
  angry: { icon: '😤', label: 'Angry', color: '#E74C3C', gradient: 'linear-gradient(135deg, #E74C3C, #922B21)' },
  chill: { icon: '🌿', label: 'Chill', color: '#667eea', gradient: 'linear-gradient(135deg, #667eea, #764ba2)' },
}

export const QUICK_MOODS = [
  { mood: 'happy', text: "I'm feeling happy and want to celebrate!" },
  { mood: 'sad', text: "I'm feeling sad and need some comforting music." },
  { mood: 'calm', text: "I want to feel calm and peaceful." },
  { mood: 'energetic', text: "I'm feeling energetic and want to dance!" },
  { mood: 'romantic', text: "I'm feeling romantic and in love." },
  { mood: 'party', text: "I want to party and have a great time!" },
  { mood: 'sleepy', text: "I'm feeling sleepy and want relaxing music." },
  { mood: 'focused', text: "I need to focus and concentrate on work." },
  { mood: 'nostalgic', text: "I feel nostalgic, play some famous old songs." },
]

export const GENRES = ['pop', 'rock', 'hip-hop', 'electronic', 'jazz', 'classical', 'r&b', 'indie', 'lo-fi', 'bollywood', 'devotional', 'folk', 'country', 'reggae', 'ambient']
export const LANGUAGES = ['english', 'hindi', 'marathi', 'punjabi', 'tamil', 'telugu', 'instrumental']

export const TRENDING_CATEGORIES = [
  { key: 'trending', label: 'Trending Now', icon: '🔥' },
  { key: 'classics', label: 'Famous Classics', icon: '📻' },
  { key: 'hindi', label: 'Hindi', icon: '🇮🇳' },
  { key: 'marathi', label: 'Marathi', icon: '🎵' },
  { key: 'punjabi', label: 'Punjabi', icon: '🥁' },
  { key: 'south', label: 'Tamil & Telugu', icon: '🎬' },
  { key: 'global', label: 'English Hits', icon: '🌎' },
]

export const LANGUAGE_CHOICES = [
  { key: 'indian', label: 'All Indian' },
  { key: 'hindi', label: 'Hindi' },
  { key: 'marathi', label: 'Marathi' },
  { key: 'punjabi', label: 'Punjabi' },
  { key: 'tamil', label: 'Tamil' },
  { key: 'telugu', label: 'Telugu' },
  { key: 'english', label: 'English' },
  { key: 'any', label: 'Everything' },
]

export function formatDuration(seconds) {
  if (!seconds) return '0:00'
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

export function formatTotalDuration(seconds) {
  if (!seconds) return '0 min'
  const hours = Math.floor(seconds / 3600)
  const mins = Math.floor((seconds % 3600) / 60)
  if (hours > 0) return `${hours}h ${mins}m`
  return `${mins} min`
}

export function formatRelativeTime(dateStr) {
  const date = new Date(dateStr)
  const now = new Date()
  const diffMin = Math.floor((now - date) / 60000)
  const diffHr = Math.floor(diffMin / 60)
  const diffDay = Math.floor(diffHr / 24)
  if (diffMin < 1) return 'just now'
  if (diffMin < 60) return `${diffMin}m ago`
  if (diffHr < 24) return `${diffHr}h ago`
  if (diffDay < 7) return `${diffDay}d ago`
  return date.toLocaleDateString()
}
