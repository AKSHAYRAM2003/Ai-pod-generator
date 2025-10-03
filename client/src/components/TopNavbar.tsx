'use client';

import { Search, Bell, User } from 'lucide-react';
import Link from 'next/link';
import { useUser } from '@/contexts/UserContext';
import { useSession } from 'next-auth/react';
import { useState, useEffect } from 'react';
import ProfilePopup from './ProfilePopup';

interface TopNavbarProps {
  onMenuClick?: () => void;
}

export default function TopNavbar({ onMenuClick }: TopNavbarProps) {
  const { user: contextUser, isAuthenticated: contextAuth, login } = useUser();
  const { data: session, status } = useSession();
  const [showProfilePopup, setShowProfilePopup] = useState(false);
  const [displayUser, setDisplayUser] = useState<any>(null);
  const [isAuth, setIsAuth] = useState(false);

  // Update display user when session or context changes
  useEffect(() => {
    console.log('🔍 TopNavbar: Auth state changed', {
      hasSession: !!session?.user,
      sessionStatus: status,
      hasContextUser: !!contextUser,
      contextAuth,
      sessionUserData: (session as any)?.userData,
      contextUserData: contextUser
    });

    // Check if user is authenticated via NextAuth session
    if (session && status === 'authenticated') {
      const backendToken = (session as any).backendToken;
      const userData = (session as any).userData;
      
      if (backendToken && userData) {
        // Store token in localStorage for API calls
        localStorage.setItem('token', backendToken);
        
        // ALWAYS sync with UserContext to ensure latest data (including avatar)
        login(userData);
        
        setDisplayUser(userData);
        setIsAuth(true);
        console.log('✅ TopNavbar: Authenticated via NextAuth session', {
          email: userData.email,
          hasAvatar: !!userData.avatar_url,
          avatarUrl: userData.avatar_url
        });
      }
    } 
    // Check if user is authenticated via context (email/password login)
    else if (contextUser && contextAuth) {
      setDisplayUser(contextUser);
      setIsAuth(true);
      console.log('✅ TopNavbar: Authenticated via UserContext', {
        email: contextUser.email,
        hasAvatar: !!contextUser.avatar_url
      });
    } 
    // No authentication - show login/signup buttons
    else {
      setDisplayUser(null);
      setIsAuth(false);
      console.log('⚠️ TopNavbar: Not authenticated - showing Login/Signup buttons');
    }
  }, [session, contextUser, contextAuth, status, login]);

  const getInitials = (firstName: string, lastName: string) => {
    if (!firstName || !lastName) return 'U';
    return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase();
  };

  const handleProfileClick = () => {
    setShowProfilePopup(true);
  };

  return (
    <>
    <header className="bg-black px-4 sm:px-6 lg:px-8 py-3 flex-shrink-0 ">
      <div className="flex items-center justify-between gap-4">
        {/* Search Bar - Responsive width */}
        <div className="flex-1 max-w-xs sm:max-w-sm md:max-w-md lg:max-w-lg xl:max-w-2xl mx-auto">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search for podcasts..."
              className="
                w-full bg-neutral-900 border border-neutral-700 rounded-full
                pl-10 pr-4 py-2 sm:py-2.5 text-sm sm:text-base text-white placeholder-gray-400
                focus:outline-none focus:border-neutral-500 focus:bg-neutral-800 
                transition-colors
              "
            />
          </div>
        </div>

        {/* Right Side - Conditional Content */}
        <div className="flex items-center space-x-1 sm:space-x-2 flex-shrink-0">
          {isAuth ? (
            <>
              {/* Bell Icon */}
              <button className="p-2 rounded-lg hover:bg-gray-800 transition-colors">
                <Bell className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
              </button>
              
              {/* Profile Avatar */}
              <button 
                onClick={handleProfileClick}
                className="w-8 h-8 sm:w-9 sm:h-9 bg-gradient-to-r from-green-500 to-green-600 rounded-full flex items-center justify-center text-white text-sm font-medium hover:from-green-600 hover:to-green-700 transition-all duration-200 shadow-lg hover:shadow-green-500/20 overflow-hidden"
              >
                {displayUser?.avatar_url ? (
                  <img 
                    key={displayUser.avatar_url}
                    src={displayUser.avatar_url} 
                    alt={`${displayUser.first_name || ''} ${displayUser.last_name || ''}`}
                    className="w-full h-full object-cover rounded-full"
                    onError={(e) => {
                      console.error('❌ Avatar failed to load:', displayUser.avatar_url);
                      e.currentTarget.style.display = 'none';
                    }}
                  />
                ) : displayUser ? (
                  getInitials(displayUser.first_name || '', displayUser.last_name || '')
                ) : (
                  <User className="w-4 h-4" />
                )}
              </button>
            </>
          ) : (
            /* Auth Buttons for Non-authenticated Users */
            <div className="flex items-center space-x-1 sm:space-x-2">
              <Link 
                href="/signin"
                className="px-2 sm:px-4 py-1.5 sm:py-2 text-sm sm:text-base text-white hover:text-gray-300 transition-colors"
              >
                Login
              </Link>
              <Link 
                href="/signup"
                className="px-3 sm:px-4 py-1.5 sm:py-2 text-sm sm:text-base bg-white text-black rounded-full font-medium hover:bg-gray-200 transition-colors"
              >
                Sign Up
              </Link>
            </div>
          )}
        </div>
      </div>
    </header>
    
    {/* Profile Popup */}
    <ProfilePopup 
      isOpen={showProfilePopup} 
      onClose={() => setShowProfilePopup(false)} 
    />
    </>
  );
}
