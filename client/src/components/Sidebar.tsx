'use client';

import { Home, Compass, BookOpen, PanelLeftOpen, PanelLeftClose, Podcast, Mic2 } from 'lucide-react';
import { useState } from 'react';
import { useRouter } from 'next/navigation';

interface SidebarProps {
  isOpen: boolean;
  setIsOpen: (isOpen: boolean) => void;
}

export default function Sidebar({ isOpen, setIsOpen }: SidebarProps) {
  const [hoveredItem, setHoveredItem] = useState<string | null>(null);
  const [activeItem, setActiveItem] = useState<string>('Home');
  const router = useRouter();

  const navigationItems = [
    { icon: Home, label: 'Home', href: '/' },
    { icon: Compass, label: 'Discover', href: '/discover' },
    { icon: BookOpen, label: 'Library', href: '/library' },
    { icon: Mic2, label: 'My Pods', href: '/mypods' },
  ];

  const handleItemClick = (itemLabel: string, href: string) => {
    setActiveItem(itemLabel);
    router.push(href);
  };

  return (
    <>
      {/* Mobile Overlay - Only for mobile screens */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-30 md:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`
        flex-shrink-0 h-full bg-black border-r border-gray-800 transition-all duration-300
        md:relative md:z-auto
        ${isOpen ? 'w-64' : 'w-16'}
        ${isOpen ? 'fixed md:relative z-40 md:z-auto' : 'relative'}
      `}>
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-800 h-20">
          {isOpen ? (
            // When open: Show logo + name on left, close button on right
            <>
              <div className="flex items-center space-x-3">
                <img src="/logo.svg" alt="Logo" className="w-9 h-9 rounded-md" />
                <span className="text-white font-semibold text-lg">GenPod</span>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="text-gray-400 hover:text-white transition-colors p-2 rounded-full hover:bg-neutral-800"
              >
                <PanelLeftClose size={30} />
              </button>
            </>
          ) : (
            // When closed: Show only open button centered
            <div className="w-full flex justify-center">
              <button
                onClick={() => setIsOpen(true)}
                className="text-gray-400 hover:text-white transition-colors p-2 rounded-full hover:bg-neutral-800"
                onMouseEnter={() => setHoveredItem('toggle')}
                onMouseLeave={() => setHoveredItem(null)}
              >
                <PanelLeftOpen size={30} />
              </button>
              
              {/* Tooltip for open button */}
              {/* {hoveredItem === 'toggle' && (
                <div className="absolute left-16 top-4 bg-gray-900 text-white px-2 py-1 rounded-md text-sm whitespace-nowrap z-50 border border-gray-700">
                  Open Sidebar
                </div>
              )} */}
            </div>
          )}
        </div>

        {/* Navigation */}
        <nav className="mt-6 px-3">
          <ul className="space-y-2">
            {navigationItems.map((item) => (
              <li key={item.label}>
                <button
                  onClick={(e) => {
                    e.preventDefault();
                    handleItemClick(item.label, item.href);
                  }}
                  className={`w-full flex items-center px-3 py-2 rounded-lg transition-all duration-200 ${
                    activeItem === item.label 
                      ? 'bg-gray-800 text-white' 
                      : 'text-gray-400 hover:text-white hover:bg-gray-800/50'
                  } ${!isOpen ? 'justify-center' : ''}`}
                  onMouseEnter={() => setHoveredItem(item.label)}
                  onMouseLeave={() => setHoveredItem(null)}
                >
                  <item.icon size={20} className="flex-shrink-0" />
                  {isOpen && (
                    <span className="ml-3 font-medium">{item.label}</span>
                  )}
                  
                  {/* Tooltip for collapsed sidebar */}
                  {!isOpen && hoveredItem === item.label && (
                    <div className="absolute left-16 bg-gray-900 text-white px-2 py-1 rounded-md text-sm whitespace-nowrap z-50 border border-gray-700">
                      {item.label}
                    </div>
                  )}
                </button>
              </li>
            ))}
          </ul>
        </nav>

        {/* Start Generate Button */}
        <div className="absolute bottom-6 left-0 right-0 px-3">
          <button 
            onClick={() => router.push('/podcast-generation')}
            className={`w-full bg-white text-black font-semibold py-3 rounded-full hover:bg-gray-200 transition-colors duration-200 flex items-center justify-center ${
              !isOpen ? 'px-2' : 'px-4'
            }`}
            onMouseEnter={() => setHoveredItem('generate')}
            onMouseLeave={() => setHoveredItem(null)}
          >
            {isOpen ? (
              <>
                <Podcast size={18} className="mr-2" />
                Start generating
              </>
            ) : (
              <Podcast size={20} />
            )}
            
            {/* Tooltip for collapsed sidebar */}
            {!isOpen && hoveredItem === 'generate' && (
              <div className="absolute left-16 bottom-0 bg-gray-900 text-white px-2 py-1 rounded-md text-sm whitespace-nowrap z-50 border border-gray-700">
                Start generating
              </div>
            )}
          </button>
        </div>
      </div>
    </>
  );
}
