'use client';

import React, { useState, useEffect, useRef } from 'react';
import { X, User, Mail, Save, Camera, Upload } from 'lucide-react';
import { useUser } from '@/contexts/UserContext';
import { useSession, signOut } from 'next-auth/react';

interface ProfilePopupProps {
  isOpen: boolean;
  onClose: () => void;
}

const ProfilePopup: React.FC<ProfilePopupProps> = ({ isOpen, onClose }) => {
  const { user, updateUser, logout } = useUser();
  const { data: session } = useSession();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [formData, setFormData] = useState({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    email: user?.email || ''
  });
  const [avatarFile, setAvatarFile] = useState<File | null>(null);
  const [avatarPreview, setAvatarPreview] = useState<string | null>(user?.avatar_url || null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Update form data when user changes
  useEffect(() => {
    if (user) {
      setFormData({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        email: user.email || ''
      });
      setAvatarPreview(user.avatar_url || null);
    }
  }, [user]);

  if (!isOpen || !user) return null;

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    setError('');
    setSuccess('');
  };

  const handleAvatarClick = () => {
    fileInputRef.current?.click();
  };

  const handleAvatarChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        setError('Please select an image file');
        return;
      }

      // Validate file size (5MB)
      if (file.size > 5 * 1024 * 1024) {
        setError('Image size must be less than 5MB');
        return;
      }

      setAvatarFile(file);
      
      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setAvatarPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
      setError('');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      // Get token from localStorage or session
      let token = localStorage.getItem('token');
      
      if (!token && session) {
        token = (session as any).backendToken;
      }
      
      if (!token) {
        setError('Authentication token not found. Please login again.');
        return;
      }

      // Create FormData for multipart/form-data
      const formDataToSend = new FormData();
      formDataToSend.append('first_name', formData.first_name);
      formDataToSend.append('last_name', formData.last_name);
      
      if (avatarFile) {
        formDataToSend.append('avatar', avatarFile);
      }

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/profile`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`
          // Don't set Content-Type - let browser set it with boundary for FormData
        },
        body: formDataToSend,
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.detail || 'Failed to update profile');
        return;
      }

      // Update user context with new data (this triggers re-render in TopNavbar)
      console.log('✅ Profile updated, updating context with:', data);
      updateUser(data);
      
      // Update local state to reflect changes immediately in the popup
      setFormData({
        first_name: data.first_name || '',
        last_name: data.last_name || '',
        email: data.email || ''
      });
      
      // Update avatar preview with server response (the compressed/processed image)
      if (data.avatar_url) {
        setAvatarPreview(data.avatar_url);
        console.log('✅ Avatar preview updated with server response');
      }
      
      setSuccess('Profile updated successfully!');
      setAvatarFile(null); // Clear file after successful upload
      
      // Don't close immediately - let user see the updated avatar
      setTimeout(() => {
        onClose();
      }, 2000); // Increased from 1500ms to 2000ms
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    // Close popup first
    onClose();
    
    // Check if user is logged in via OAuth
    if (session) {
      // Clear user context first
      logout();
      // Then sign out from NextAuth (this will redirect)
      await signOut({ callbackUrl: '/', redirect: true });
    } else {
      // Regular email/password logout
      logout();
      window.location.href = '/';
    }
  };

  const getInitials = (firstName: string, lastName: string) => {
    if (!firstName || !lastName) return 'U';
    return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div className="w-full max-w-md bg-neutral-900 rounded-2xl border border-neutral-700 shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-neutral-700">
          <h2 className="text-xl font-semibold text-white">Edit Profile</h2>
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-neutral-800 transition-colors"
          >
            <X className="w-5 h-5 text-gray-400" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="p-3 rounded-lg bg-red-500/10 border border-red-400/30 text-red-400 text-sm">
              {error}
            </div>
          )}

          {success && (
            <div className="p-3 rounded-lg bg-green-500/10 border border-green-400/30 text-green-400 text-sm">
              {success}
            </div>
          )}

          {/* Avatar Upload Section */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Profile Picture
            </label>
            <div className="flex items-center gap-4">
              {/* Avatar Preview */}
              <div className="relative">
                <div 
                  onClick={handleAvatarClick}
                  className="w-20 h-20 rounded-full bg-gradient-to-r from-green-500 to-green-600 flex items-center justify-center text-white text-2xl font-medium overflow-hidden cursor-pointer hover:from-green-600 hover:to-green-700 transition-all duration-200 shadow-lg"
                >
                  {avatarPreview ? (
                    <img 
                      key={avatarPreview}
                      src={avatarPreview} 
                      alt="Avatar" 
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    getInitials(formData.first_name, formData.last_name)
                  )}
                </div>
                <button
                  type="button"
                  onClick={handleAvatarClick}
                  className="absolute bottom-0 right-0 p-1.5 bg-green-600 rounded-full text-white hover:bg-green-700 transition-colors shadow-lg"
                >
                  <Camera className="w-3 h-3" />
                </button>
              </div>

              {/* Upload Button */}
              <div className="flex-1">
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleAvatarChange}
                  className="hidden"
                />
                <button
                  type="button"
                  onClick={handleAvatarClick}
                  className="w-full flex items-center justify-center gap-2 px-4 py-2 border border-neutral-600 text-gray-300 rounded-lg hover:bg-neutral-800 transition-colors"
                >
                  <Upload className="w-4 h-4" />
                  {avatarFile ? 'Change Photo' : 'Upload Photo'}
                </button>
                <p className="text-xs text-gray-400 mt-1">
                  JPG, PNG or GIF. Max 5MB
                </p>
              </div>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              First Name
            </label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                name="first_name"
                value={formData.first_name}
                onChange={handleInputChange}
                className="w-full bg-neutral-800 border border-neutral-600 rounded-lg pl-10 pr-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:border-green-500 focus:bg-neutral-700 transition-colors"
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Last Name
            </label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                name="last_name"
                value={formData.last_name}
                onChange={handleInputChange}
                className="w-full bg-neutral-800 border border-neutral-600 rounded-lg pl-10 pr-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:border-green-500 focus:bg-neutral-700 transition-colors"
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Email Address
            </label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                className="w-full bg-neutral-800 border border-neutral-600 rounded-lg pl-10 pr-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:border-green-500 focus:bg-neutral-700 transition-colors"
                required
                disabled // Email usually shouldn't be editable after verification
              />
            </div>
            <p className="text-xs text-gray-400 mt-1">Email cannot be changed after verification</p>
          </div>

          {/* Buttons */}
          <div className="flex space-x-3 pt-4">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 flex items-center justify-center gap-2 bg-gradient-to-r from-green-600 to-green-500 hover:from-green-700 hover:to-green-600 text-white font-medium py-3 px-4 rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Save className="w-4 h-4" />
              {loading ? 'Saving...' : 'Save Changes'}
            </button>
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-3 border border-neutral-600 text-gray-300 rounded-lg hover:bg-neutral-800 transition-colors"
            >
              Cancel
            </button>
          </div>

          {/* Logout Button */}
          <div className="pt-4 border-t border-neutral-700">
            <button
              type="button"
              onClick={handleLogout}
              className="w-full py-3 text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded-lg transition-colors"
            >
              Sign Out
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ProfilePopup;
