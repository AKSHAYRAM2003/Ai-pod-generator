'use client';

import { Play, Pause, SkipBack, SkipForward, Volume2, VolumeX, Heart } from 'lucide-react';
import { useState, useEffect, useRef } from 'react';

const MediaController = () => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(45);
  const [duration, setDuration] = useState(180); // 3 minutes in seconds
  const [volume, setVolume] = useState(65);
  const [isLiked, setIsLiked] = useState(false);
  const progressBarRef = useRef<HTMLDivElement>(null);
  const volumeBarRef = useRef<HTMLDivElement>(null);

  // Currently playing track info
  const currentTrack = {
    title: "The Rise of Generative Audio",
    podcast: "AI Voices Podcast",
    avatar: "bg-gradient-to-br from-emerald-400 via-cyan-500 to-blue-500"
  };

  // Format time in MM:SS
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Progress bar percentage
  const progress = (currentTime / duration) * 100;

  // Auto increment time when playing
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isPlaying && currentTime < duration) {
      interval = setInterval(() => {
        setCurrentTime(prev => prev + 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isPlaying, currentTime, duration]);

  const togglePlayPause = () => {
    setIsPlaying(!isPlaying);
  };

  const handlePrevious = () => {
    setCurrentTime(0);
  };

  const handleNext = () => {
    setCurrentTime(0);
    // Logic to skip to next track would go here
  };

  const [isDragging, setIsDragging] = useState(false);
  const [dragProgress, setDragProgress] = useState(0);

  const handleProgressClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!progressBarRef.current) return;
    const rect = progressBarRef.current.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const newProgress = Math.max(0, Math.min(100, (clickX / rect.width) * 100));
    const newTime = Math.floor((newProgress / 100) * duration);
    setCurrentTime(newTime);
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    e.preventDefault();
    setIsDragging(true);
    setDragProgress(progress);
  };

  const handleMouseMove = (e: MouseEvent) => {
    if (!isDragging || !progressBarRef.current) return;
    
    const rect = progressBarRef.current.getBoundingClientRect();
    const moveX = e.clientX - rect.left;
    const newProgress = Math.max(0, Math.min(100, (moveX / rect.width) * 100));
    setDragProgress(newProgress);
  };

  const handleMouseUp = () => {
    if (isDragging) {
      const newTime = Math.floor((dragProgress / 100) * duration);
      setCurrentTime(newTime);
      setIsDragging(false);
    }
  };

  // Volume control states and handlers
  const [isVolumeDragging, setIsVolumeDragging] = useState(false);
  const [dragVolume, setDragVolume] = useState(0);

  const handleVolumeClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!volumeBarRef.current) return;
    const rect = volumeBarRef.current.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const newVolume = Math.max(0, Math.min(100, (clickX / rect.width) * 100));
    setVolume(newVolume);
  };

  const handleVolumeMouseDown = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsVolumeDragging(true);
    setDragVolume(volume);
  };

  const handleVolumeMouseMove = (e: MouseEvent) => {
    if (!isVolumeDragging || !volumeBarRef.current) return;
    
    const rect = volumeBarRef.current.getBoundingClientRect();
    const moveX = e.clientX - rect.left;
    const newVolume = Math.max(0, Math.min(100, (moveX / rect.width) * 100));
    setDragVolume(newVolume);
  };

  const handleVolumeMouseUp = () => {
    if (isVolumeDragging) {
      setVolume(dragVolume);
      setIsVolumeDragging(false);
    }
  };

  const toggleMute = () => {
    setVolume(volume === 0 ? 65 : 0);
  };

  // Add mouse event listeners for dragging
  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    }
    
    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging, dragProgress]);

  // Add mouse event listeners for volume dragging
  useEffect(() => {
    if (isVolumeDragging) {
      document.addEventListener('mousemove', handleVolumeMouseMove);
      document.addEventListener('mouseup', handleVolumeMouseUp);
    }
    
    return () => {
      document.removeEventListener('mousemove', handleVolumeMouseMove);
      document.removeEventListener('mouseup', handleVolumeMouseUp);
    };
  }, [isVolumeDragging, dragVolume]);

  return (
    <div className="relative backdrop-blur-xl bg-gradient-to-r from-white/10 via-white/5 to-white/10 border border-white/20 rounded-2xl shadow-2xl shadow-black/30 mx-4 mb-4 overflow-hidden">
      {/* Subtle gradient overlay for extra depth */}
      <div className="absolute inset-0 bg-gradient-to-br from-transparent via-white/5 to-transparent pointer-events-none"></div>
      
      <div className="relative px-6 py-4">
        <div className="flex items-center justify-between max-w-full gap-4">
          {/* Currently Playing Info - Left Side */}
          <div className="flex items-center space-x-3 flex-shrink-0 min-w-0 max-w-[280px] lg:max-w-[320px]">
            <div className={`w-14 h-14 ${currentTrack.avatar} rounded-lg flex items-center justify-center flex-shrink-0 shadow-lg`}>
              <div className="w-7 h-7 bg-white/20 rounded-md flex items-center justify-center">
                <div className="w-4 h-4 bg-white/60 rounded-sm"></div>
              </div>
            </div>
            <div className="min-w-0 flex-1">
              <h4 className="text-white font-semibold text-sm truncate leading-tight">
                {currentTrack.title}
              </h4>
              <p className="text-gray-400 text-xs truncate">
                {currentTrack.podcast}
              </p>
            </div>
            <button
              onClick={() => setIsLiked(!isLiked)}
              className={`p-2 rounded-full transition-all duration-200 hover:scale-110 backdrop-blur-sm hover:bg-white/10 ${
                isLiked 
                  ? 'text-green-400 hover:text-green-300 bg-green-400/20' 
                  : 'text-white/70 hover:text-white'
              }`}
            >
              <Heart size={16} fill={isLiked ? 'currentColor' : 'none'} />
            </button>
          </div>

          {/* Control Section - Center */}
          <div className="flex flex-col items-center space-y-3 flex-1 max-w-2xl">
            {/* Control Buttons */}
            <div className="flex items-center justify-center space-x-6">
              <button
                onClick={handlePrevious}
                className="text-white/70 hover:text-white transition-all duration-200 p-2 hover:scale-110 rounded-full hover:bg-white/10 backdrop-blur-sm"
              >
                <SkipBack size={20} />
              </button>
              
              <button
                onClick={togglePlayPause}
                className="bg-white/90 backdrop-blur-sm text-black rounded-full p-3 hover:scale-110 hover:bg-white transition-all duration-200 shadow-xl shadow-white/20 hover:shadow-2xl hover:shadow-white/30"
              >
                {isPlaying ? <Pause size={20} /> : <Play size={20} className="ml-0.5" />}
              </button>
              
              <button
                onClick={handleNext}
                className="text-white/70 hover:text-white transition-all duration-200 p-2 hover:scale-110 rounded-full hover:bg-white/10 backdrop-blur-sm"
              >
                <SkipForward size={20} />
              </button>
            </div>

            {/* Progress Bar and Time */}
            <div className="flex items-center space-x-3 w-full max-w-lg">
              <div className="text-gray-400 text-xs font-mono tabular-nums min-w-[35px]">
                {formatTime(currentTime)}
              </div>
              
              <div 
                ref={progressBarRef}
                className="relative flex-1 h-1 bg-white/20 rounded-full cursor-pointer group hover:h-1.5 transition-all duration-200 backdrop-blur-sm"
                onClick={handleProgressClick}
              >
                {/* Background track */}
                <div className="absolute inset-0 bg-white/20 rounded-full backdrop-blur-sm" />
                
                {/* Progress track */}
                <div 
                  className="h-full bg-gradient-to-r from-emerald-400 via-cyan-400 to-blue-400 rounded-full transition-all duration-100 group-hover:from-emerald-300 group-hover:via-cyan-300 group-hover:to-blue-300 relative shadow-lg shadow-cyan-500/20"
                  style={{ width: `${isDragging ? dragProgress : progress}%` }}
                >
                  {/* Draggable Circle Pointer */}
                  <div 
                    className={`absolute right-0 top-1/2 w-3 h-3 bg-white rounded-full shadow-xl shadow-cyan-500/30 cursor-grab active:cursor-grabbing transition-all duration-200 transform -translate-y-1/2 ${
                      isDragging ? 'opacity-100 scale-125' : 'opacity-0 scale-75 group-hover:opacity-100 group-hover:scale-100'
                    }`}
                    style={{ transform: 'translate(50%, -50%)' }}
                    onMouseDown={handleMouseDown}
                  >
                    <div className="absolute inset-0 bg-white rounded-full group-hover:shadow-lg group-hover:shadow-cyan-400/40 transition-all duration-200" />
                  </div>
                </div>
              </div>
              
              <div className="text-gray-400 text-xs font-mono tabular-nums min-w-[35px]">
                {formatTime(duration)}
              </div>
            </div>
          </div>

          {/* Volume Control - Right Side */}
          <div className="hidden lg:flex items-center space-x-3 flex-shrink-0 w-36">
            <button
              onClick={toggleMute}
              className="text-white/70 hover:text-white transition-all duration-200 p-2 rounded-full hover:bg-white/10 backdrop-blur-sm hover:scale-110"
            >
              {volume === 0 ? <VolumeX size={18} /> : <Volume2 size={18} />}
            </button>
            
            <div 
              ref={volumeBarRef}
              className="relative flex-1 h-1 bg-white/20 rounded-full cursor-pointer group hover:h-1.5 transition-all duration-200 backdrop-blur-sm"
              onClick={handleVolumeClick}
            >
              {/* Background track */}
              <div className="absolute inset-0 bg-white/20 rounded-full backdrop-blur-sm" />
              
              {/* Volume track */}
              <div 
                className="h-full bg-gradient-to-r from-purple-400 to-pink-400 rounded-full transition-all duration-100 group-hover:from-purple-300 group-hover:to-pink-300 relative shadow-lg shadow-purple-500/20"
                style={{ width: `${isVolumeDragging ? dragVolume : volume}%` }}
              >
                {/* Volume Circle Pointer */}
                <div 
                  className={`absolute right-0 top-1/2 w-3 h-3 bg-white rounded-full shadow-xl shadow-purple-500/30 cursor-grab active:cursor-grabbing transition-all duration-200 transform -translate-y-1/2 ${
                    isVolumeDragging ? 'opacity-100 scale-125' : 'opacity-0 scale-75 group-hover:opacity-100 group-hover:scale-100'
                  }`}
                  style={{ transform: 'translate(50%, -50%)' }}
                  onMouseDown={handleVolumeMouseDown}
                >
                  <div className="absolute inset-0 bg-white rounded-full group-hover:shadow-lg group-hover:shadow-purple-400/40 transition-all duration-200" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MediaController;
