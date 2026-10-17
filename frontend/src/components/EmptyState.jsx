export default function EmptyState({ icon: Icon, title, message, action }) {
  return (
    <div className="empty-state">
      {Icon && <Icon size={22} />}
      <strong>{title}</strong>
      <span>{message}</span>
      {action}
    </div>
  )
}
