export function SongListSkeleton({ count = 5 }) {
  return <div className="song-list">{Array.from({ length: count }, (_, i) => <div key={i} className="skeleton" style={{height:68}} />)}</div>
}

export function PlaylistGridSkeleton({ count = 4 }) {
  return <div className="playlist-grid">{Array.from({ length: count }, (_, i) => <div key={i} className="skeleton" style={{height:230}} />)}</div>
}
