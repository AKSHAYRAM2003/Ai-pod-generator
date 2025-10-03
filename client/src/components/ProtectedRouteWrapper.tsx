'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useUser } from '@/contexts/UserContext';
import { useSession } from 'next-auth/react';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { isAuthenticated, user } = useUser();
  const { data: session, status } = useSession();
  const router = useRouter();
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    console.log('[ProtectedRoute] Auth check:', { 
      isAuthenticated, 
      hasUser: !!user,
      sessionStatus: status, 
      hasSession: !!session 
    });

    // Wait for session to load
    if (status === 'loading') {
      console.log('[ProtectedRoute] Session still loading...');
      return;
    }

    // Check if user is authenticated via either method
    const isAuth = isAuthenticated || (session && status === 'authenticated');

    console.log('[ProtectedRoute] Final auth decision:', isAuth);

    // Mark checking as complete once session is loaded
    setIsChecking(false);

    if (!isAuth) {
      console.log('[ProtectedRoute] Not authenticated, redirecting to signin');
      // Small delay to prevent flash of content
      setTimeout(() => {
        router.push('/signin');
      }, 100);
    } else {
      console.log('[ProtectedRoute] Authenticated, showing content');
    }
  }, [isAuthenticated, session, status, router, user]);

  // Show loading state while checking authentication
  if (status === 'loading' || isChecking) {
    return (
      <div className="flex items-center justify-center h-screen bg-black">
        <div className="flex flex-col items-center gap-4">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-500"></div>
          <div className="text-white text-xl">Verifying authentication...</div>
        </div>
      </div>
    );
  }

  // Double-check authentication before rendering
  const isAuth = isAuthenticated || (session && status === 'authenticated');
  if (!isAuth) {
    return (
      <div className="flex items-center justify-center h-screen bg-black">
        <div className="text-white text-xl">Redirecting to login...</div>
      </div>
    );
  }

  return <>{children}</>;
}
