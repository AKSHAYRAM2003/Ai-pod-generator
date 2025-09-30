'use client';

import { Search, Bell } from 'lucide-react';

interface TopNavbarProps {
  onMenuClick?: () => void;
}

export default function TopNavbar({ onMenuClick }: TopNavbarProps) {
  return (
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

        {/* Right Side - Bell Icon and Auth Buttons */}
        <div className="flex items-center space-x-2 sm:space-x-4 flex-shrink-0">
          <button className="p-2 rounded-lg hover:bg-gray-800 transition-colors">
            <Bell className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
          </button>
          
          <div className="flex items-center space-x-1 sm:space-x-2">
            <button className="px-2 sm:px-4 py-1.5 sm:py-2 text-sm sm:text-base text-white hover:text-gray-300 transition-colors">
              Login
            </button>
            <button className="px-3 sm:px-4 py-1.5 sm:py-2 text-sm sm:text-base bg-white text-black rounded-full font-medium hover:bg-gray-200 transition-colors">
              Sign Up
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
