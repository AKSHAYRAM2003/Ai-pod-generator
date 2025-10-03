'use client';

import { useRouter } from 'next/navigation';
import { useUser } from '@/contexts/UserContext';
import { useEffect } from 'react';
import ProfilePopup from '@/components/ProfilePopup';

export default function ProfilePage() {
  const router = useRouter();
  const { isAuthenticated } = useUser();

  useEffect(() => {
    // Redirect to home if not authenticated
    if (!isAuthenticated) {
      router.push('/');
    }
  }, [isAuthenticated, router]);

  const handleClose = () => {
    router.push('/'); // Navigate back to home when closing
  };

  if (!isAuthenticated) {
    return null; // Don't render anything while redirecting
  }

  return (
    <div className="fixed inset-0 z-50">
      <ProfilePopup 
        isOpen={true} 
        onClose={handleClose}
      />
    </div>
  );
}
