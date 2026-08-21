import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { resetSession } from '../../services/api';
import {
  Bot,
  TrendingUp,
  History as HistoryIcon,
  User as UserIcon,
  LogOut,
  RotateCcw,
  Loader2,
} from 'lucide-react';

const NAV_ITEMS = [
  {
    to: '/tutor',
    label: 'Tutor',
    icon: Bot,
    description: 'Code workspace',
  },
  {
    to: '/progress',
    label: 'Progress',
    icon: TrendingUp,
    description: 'Mastery & insights',
  },
  {
    to: '/history',
    label: 'History',
    icon: HistoryIcon,
    description: 'Submissions',
  },
  {
    to: '/profile',
    label: 'Profile',
    icon: UserIcon,
    description: 'Account',
  },
];

export default function Navigation() {
  const { user, displayName, signOut, loading } = useAuth();
  const navigate = useNavigate();
  const [isLoggingOut, setIsLoggingOut] = React.useState(false);
  const [isResetting, setIsResetting] = React.useState(false);

  const handleLogout = async () => {
    setIsLoggingOut(true);
    try {
      await signOut();
      navigate('/login', { replace: true });
    } catch (err) {
      console.error('[Navigation] Logout failed:', err);
    } finally {
      setIsLoggingOut(false);
    }
  };

  const handleReset = async () => {
    setIsResetting(true);
    try {
      await resetSession();
      window.location.reload();
    } catch (err) {
      console.error('[Navigation] Reset failed:', err);
      alert('Failed to reset session. Please refresh the page manually.');
    } finally {
      setIsResetting(false);
    }
  };

  const initials = React.useMemo(() => {
    const name = displayName || 'Learner';
    return name
      .split(/[\s_.-]/)
      .filter(Boolean)
      .slice(0, 2)
      .map((p) => p[0]?.toUpperCase() || '')
      .join('') || 'L';
  }, [displayName]);

  return (
    <aside className="sidebar" aria-label="Primary navigation">
      <div className="sidebar-inner">
        <div className="sidebar-brand">
          <span className="brand-badge" style={{ fontSize: 15, padding: '5px 9px' }}>
            LBL
          </span>
          <div className="sidebar-brand-text">
            <span className="sidebar-brand-title">LineByLine</span>
            <span className="sidebar-brand-sub">AI Code Tutor</span>
          </div>
        </div>

        <nav className="sidebar-nav" role="navigation">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `nav-item${isActive ? ' active' : ''}`
                }
              >
                {({ isActive }) => (
                  <>
                    <span
                      className={`nav-item-accent${isActive ? ' visible' : ''}`}
                      aria-hidden="true"
                    />
                    <Icon size={18} className="nav-item-icon" aria-hidden="true" />
                    <span className="nav-item-labels">
                      <span className="nav-item-label">{item.label}</span>
                      <span className="nav-item-desc">{item.description}</span>
                    </span>
                  </>
                )}
              </NavLink>
            );
          })}
        </nav>

        <div className="sidebar-spacer" />

        <div className="sidebar-footer">
          <button
            className="sidebar-footer-btn"
            onClick={handleReset}
            disabled={isResetting || loading}
            title="Clear server-side session state"
          >
            {isResetting ? (
              <Loader2 size={15} style={{ animation: 'spin 0.8s linear infinite' }} />
            ) : (
              <RotateCcw size={15} />
            )}
            <span>{isResetting ? 'Resetting…' : 'Reset Session'}</span>
          </button>

          {user && !loading && (
            <div className="sidebar-user">
              <div className="sidebar-user-avatar" title={user.email || ''}>
                {initials}
              </div>
              <div className="sidebar-user-info">
                <span className="sidebar-user-name">{displayName}</span>
                <span className="sidebar-user-email">
                  {user.email || 'Signed in'}
                </span>
              </div>
            </div>
          )}

          <button
            className="sidebar-footer-btn signout"
            onClick={handleLogout}
            disabled={isLoggingOut || loading}
          >
            {isLoggingOut ? (
              <Loader2 size={15} style={{ animation: 'spin 0.8s linear infinite' }} />
            ) : (
              <LogOut size={15} />
            )}
            <span>{isLoggingOut ? 'Signing out…' : 'Sign Out'}</span>
          </button>
        </div>
      </div>
    </aside>
  );
}
