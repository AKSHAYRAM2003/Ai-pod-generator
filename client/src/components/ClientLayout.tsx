'use client';

import { useState } from 'react';
import { usePathname } from 'next/navigation';
import { SessionProvider } from 'next-auth/react';
import Sidebar from './Sidebar';
import TopNavbar from './TopNavbar';
import MediaController from './MediaController';
import { UserProvider } from '@/contexts/UserContext';

interface ClientLayoutProps {
  children: React.ReactNode;
}

export default function ClientLayout({ children }: ClientLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(true); // Default to open on desktop
  const pathname = usePathname();
  
  // Check if current page is an auth page or standalone page
  const isAuthPage = pathname === '/signup' || pathname === '/signin';
  const isStandalonePage = pathname === '/profile';
  
  // For auth pages and standalone pages, render children without layout components but with providers
  if (isAuthPage || isStandalonePage) {
    return (
      <SessionProvider>
        <UserProvider>{children}</UserProvider>
      </SessionProvider>
    );
  }

  return (
    <SessionProvider>
      <UserProvider>
    <div className="h-screen flex overflow-hidden bg-black">
      {/* Sidebar */}
      <Sidebar isOpen={sidebarOpen} setIsOpen={setSidebarOpen} />
      
      {/* Main Content Area - Adjusts based on sidebar state */}
      <div className="flex-1 flex flex-col min-w-0 transition-all duration-300">
        {/* Top Navbar */}
        <TopNavbar 
          onMenuClick={() => setSidebarOpen(!sidebarOpen)} 
        />
        
        {/* Page Content with Media Controller */}
        <div className="flex-1 flex flex-col overflow-hidden bg-black">
          <div className="flex-1 overflow-auto">
            {children}
          </div>
          
          {/* Media Controller - Within main content area */}
          <div className="flex-shrink-0">
            <MediaController />
          </div>
        </div>
      </div>
    </div>
    </UserProvider>
    </SessionProvider>
  );
}
