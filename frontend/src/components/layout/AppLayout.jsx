import React from 'react';
import { Outlet } from 'react-router-dom';
import Navigation from './Navigation';
import MobileNavigation from './MobileNavigation';
import ErrorBoundary from '../ErrorBoundary';

export default function AppLayout() {
  return (
    <div className="app-shell">
      <Navigation />
      <MobileNavigation />

      <div className="content-area">
        <main className="content-main" id="main-content">
          <ErrorBoundary>
            <Outlet />
          </ErrorBoundary>
        </main>
      </div>
    </div>
  );
}
