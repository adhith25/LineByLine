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
  Menu,
  X,
  Loader2,
} from 'lucide-react';

const MOBILE_NAV = [
  { to: '/tutor', label: 'Tutor', icon: Bot },
  { to: '/progress', label: 'Progress', icon: TrendingUp },
  { to: '/history', label: 'History', icon: HistoryIcon },
  { to: '/profile', label: 'Profile', icon: UserIcon },
];

export default function MobileNavigation() {
  const { displayName, signOut, user, loading } = useAuth();
  const navigate = useNavigate();
  const [drawerOpen, setDrawerOpen] = React.useState(false);
  const [isLoggingOut, setIsLoggingOut] = React.useState(false);
  const [isResetting, setIsResetting] = React.useState(false);

  const closeDrawer = () => setDrawerOpen(false);

  const handleLogout = async () => {
    setIsLoggingOut(true);
    try {
      await signOut();
      navigate('/login', { replace: true });
    } catch (err) {
      console.error('[MobileNav] Logout failed:', err);
    } finally {
      setIsLoggingOut(false);
      setDrawerOpen(false);
    }
  };

  const handleReset = async () => {
    setIsResetting(true);
    try {
      await resetSession();
      window.location.reload();
    } catch (err) {
      console.error('[MobileNav] Reset failed:', err);
      alert('Failed to reset session. Please refresh manually.');
    } finally {
      setIsResetting(false);
    }
  };

  return (
    <>
      <div className="mobile-topbar" role="banner">
        <button
          className="mobile-menu-btn"
          onClick={() => setDrawerOpen((o) => !o)}
          aria-label="Open menu"
          aria-expanded={drawerOpen}
        >
          {drawerOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
        <div className="mobile-topbar-brand">
          <span className="brand-badge" style={{ fontSize: 13, padding: '3px 7px' }}>
            LBL
          </span>
          <span className="mobile-topbar-title">LineByLine</span>
        </div>
        <div className="mobile-topbar-spacer" />
      </div>

      {drawerOpen && (
        <div
          className="mobile-drawer-backdrop"
          onClick={closeDrawer}
          aria-hidden="true"
        />
      )}

      <aside className={`mobile-drawer${drawerOpen ? ' open' : ''}`} aria-label="Mobile navigation">
        <div className="mobile-drawer-header">
          <div className="sidebar-brand">
            <span className="brand-badge" style={{ fontSize: 14, padding: '4px 8px' }}>
              LBL
            </span>
            <div className="sidebar-brand-text">
              <span className="sidebar-brand-title">LineByLine</span>
              <span className="sidebar-brand-sub">AI Code Tutor</span>
            </div>
          </div>
        </div>

        <nav className="mobile-drawer-nav" role="navigation">
          {MOBILE_NAV.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                onClick={closeDrawer}
                className={({ isActive }) =>
                  `mobile-drawer-item${isActive ? ' active' : ''}`
                }
              >
                <Icon size={18} />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>

        <div className="mobile-drawer-footer">
          {user && !loading && (
            <div className="sidebar-user" style={{ paddingBottom: 12 }}>
              <div
                className="sidebar-user-avatar"
                title={user.email || ''}
                style={{ width: 32, height: 32, fontSize: 12 }}
              >
                {(displayName || 'L')[0]?.toUpperCase()}
              </div>
              <div className="sidebar-user-info">
                <span className="sidebar-user-name">{displayName}</span>
                <span className="sidebar-user-email">{user.email || ''}</span>
              </div>
            </div>
          )}

          <button
            className="mobile-drawer-action"
            onClick={handleReset}
            disabled={isResetting}
          >
            {isResetting ? (
              <Loader2 size={15} style={{ animation: 'spin 0.8s linear infinite' }} />
            ) : (
              <RotateCcw size={15} />
            )}
            <span>{isResetting ? 'Resetting…' : 'Reset Session'}</span>
          </button>

          <button
            className="mobile-drawer-action signout"
            onClick={handleLogout}
            disabled={isLoggingOut}
          >
            {isLoggingOut ? (
              <Loader2 size={15} style={{ animation: 'spin 0.8s linear infinite' }} />
            ) : (
              <LogOut size={15} />
            )}
            <span>{isLoggingOut ? 'Signing out…' : 'Sign Out'}</span>
          </button>
        </div>
      </aside>

      <nav className="mobile-tabbar" role="navigation" aria-label="Tab navigation">
        {MOBILE_NAV.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `mobile-tabbar-item${isActive ? ' active' : ''}`
              }
            >
              <Icon size={20} aria-hidden="true" />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </nav>
    </>
  );
}
