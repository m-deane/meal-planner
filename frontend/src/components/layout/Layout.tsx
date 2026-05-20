import React from 'react';
import { Outlet } from 'react-router-dom';
import { Navigation } from './Navigation';

export const Layout: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 overflow-x-hidden">
      <Navigation />
      <main className="pb-16 md:pb-0">
        <Outlet />
      </main>
    </div>
  );
};

export default Layout;
