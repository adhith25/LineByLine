import React from 'react';

export default function EmptyState({
  icon,
  title,
  description,
  action,
  actionLabel,
  onAction,
}) {
  return (
    <div className="empty-state-page">
      <div className="empty-state-card">
        {icon && <div className="empty-state-icon" aria-hidden="true">{icon}</div>}
        {title && <h2 className="empty-state-title">{title}</h2>}
        {description && (
          <p className="empty-state-desc">{description}</p>
        )}
        {actionLabel && onAction && (
          <button className="btn-primary" style={{ marginTop: 20, width: 'auto', padding: '10px 22px' }} onClick={onAction}>
            {action}
            <span>{actionLabel}</span>
          </button>
        )}
      </div>
    </div>
  );
}
