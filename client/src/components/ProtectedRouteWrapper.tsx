'use client';

import { useEffect } from 'react';
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

  useEffect(() => {
    // Wait for session to load
    if (status === 'loading') return;

    // Check if user is authenticated via either method
    const isAuth = isAuthenticated || (session && status === 'authenticated');

    if (!isAuth) {
      // Redirect to signin if not authenticated
      router.push('/signin');
    }
  }, [isAuthenticated, session, status, router]);

  // Show loading state while checking authentication
  if (status === 'loading' || (!isAuthenticated && !session)) {
    return (
      <div className="flex items-center justify-center h-screen bg-black">
        <div className="text-white text-xl">Loading...</div>
      </div>
    );
  }

  return <>{children}</>;
}
