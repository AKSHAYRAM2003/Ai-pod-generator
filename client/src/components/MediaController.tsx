'use client';

import { Play, Pause, SkipBack, SkipForward, Volume2, VolumeX, Heart } from 'lucide-react';
import { useState, useEffect, useRef } from 'react';
import { useAudioPlayer } from '@/contexts/AudioPlayerContext';

const MediaController = () => {
  const { 
    currentPodcast, 
    isPlaying, 
    currentTime, 
    duration, 
    volume,
    togglePlayPause, 
    seek, 
    setVolume 
  } = useAudioPlayer();

  const [isLiked, setIsLiked] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [dragProgress, setDragProgress] = useState(0);
  const [isVolumeDragging, setIsVolumeDragging] = useState(false);
  const [dragVolume, setDragVolume] = useState(0);
  
  const progressBarRef = useRef<HTMLDivElement>(null);
  const volumeBarRef = useRef<HTMLDivElement>(null);

  // Format time in MM:SS
  const formatTime = (seconds: number) => {
    if (isNaN(seconds) || !isFinite(seconds)) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Progress bar percentage
  const progress = duration > 0 ? (currentTime / duration) * 100 : 0;

  const handlePrevious = () => {
    seek(0);
  };

  const handleNext = () => {
    seek(0);
    // Logic to skip to next track would go here
  };

  const handleProgressClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!progressBarRef.current) return;
    const rect = progressBarRef.current.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const newProgress = Math.max(0, Math.min(100, (clickX / rect.width) * 100));
    const newTime = (newProgress / 100) * duration;
    seek(newTime);
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
      const newTime = (dragProgress / 100) * duration;
      seek(newTime);
      setIsDragging(false);
    }
  };

  const handleVolumeClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!volumeBarRef.current) return;
    const rect = volumeBarRef.current.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const newVolume = Math.max(0, Math.min(100, (clickX / rect.width) * 100));
    setVolume(newVolume);
  };

  const handleVolumeMouseDown = (e: React.MouseEvent) => {
    e.preventDefault();
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

  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [isDragging, dragProgress, duration]);

  useEffect(() => {
    if (isVolumeDragging) {
      document.addEventListener('mousemove', handleVolumeMouseMove);
      document.addEventListener('mouseup', handleVolumeMouseUp);
      return () => {
        document.removeEventListener('mousemove', handleVolumeMouseMove);
        document.removeEventListener('mouseup', handleVolumeMouseUp);
      };
    }
  }, [isVolumeDragging, dragVolume]);

  const toggleMute = () => {
    setVolume(volume > 0 ? 0 : 65);
  };

  // Don't show controller if no podcast is playing
  if (!currentPodcast) {
    return null;
  }

  return (
    <div className="w-full bg-zinc-900/95 backdrop-blur-lg border-t border-white/10 px-4 py-3">
      <div className="max-w-screen-2xl mx-auto">
        {/* Progress Bar */}
        <div className="mb-3">
          <div
            ref={progressBarRef}
            className="h-1 bg-white/10 rounded-full cursor-pointer group relative"
            onClick={handleProgressClick}
          >
            <div 
              className="h-full bg-white rounded-full transition-all group-hover:bg-white/90 relative"
              style={{ width: `${isDragging ? dragProgress : progress}%` }}
            >
              {/* Draggable knob */}
              <div 
                className="absolute right-0 top-1/2 -translate-y-1/2 w-3 h-3 bg-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity cursor-grab active:cursor-grabbing shadow-lg"
                onMouseDown={handleMouseDown}
              />
            </div>
          </div>
          <div className="flex justify-between text-xs text-gray-400 mt-1">
            <span>{formatTime(currentTime)}</span>
            <span>{formatTime(duration)}</span>
          </div>
        </div>

        <div className="flex items-center justify-between gap-4">
          {/* Left: Track Info */}
          <div className="flex items-center gap-3 min-w-0 flex-1">
            <div className="w-12 h-12 bg-gradient-to-br from-white/10 to-white/5 rounded-lg flex items-center justify-center flex-shrink-0 text-xl border border-white/10">
              {currentPodcast.category?.icon || '🎙️'}
            </div>
            <div className="min-w-0 flex-1">
              <div className="text-white font-medium text-sm truncate">
                {currentPodcast.topic}
              </div>
              <div className="text-gray-400 text-xs truncate">
                {currentPodcast.category?.name || 'Podcast'}
              </div>
            </div>
            <button 
              onClick={() => setIsLiked(!isLiked)}
              className="text-gray-400 hover:text-white transition-colors flex-shrink-0"
            >
              <Heart className={`w-5 h-5 ${isLiked ? 'fill-red-500 text-red-500' : ''}`} />
            </button>
          </div>

          {/* Center: Playback Controls */}
          <div className="flex items-center gap-4">
            <button 
              onClick={handlePrevious}
              className="text-gray-400 hover:text-white transition-colors"
            >
              <SkipBack className="w-5 h-5" />
            </button>
            
            <button 
              onClick={togglePlayPause}
              className="w-10 h-10 bg-white hover:bg-white/90 rounded-full flex items-center justify-center text-black transition-all hover:scale-105"
            >
              {isPlaying ? (
                <Pause className="w-5 h-5" />
              ) : (
                <Play className="w-5 h-5 ml-0.5" />
              )}
            </button>
            
            <button 
              onClick={handleNext}
              className="text-gray-400 hover:text-white transition-colors"
            >
              <SkipForward className="w-5 h-5" />
            </button>
          </div>

          {/* Right: Volume Control */}
          <div className="flex items-center gap-3 flex-1 justify-end">
            <button 
              onClick={toggleMute}
              className="text-gray-400 hover:text-white transition-colors"
            >
              {volume === 0 ? (
                <VolumeX className="w-5 h-5" />
              ) : (
                <Volume2 className="w-5 h-5" />
              )}
            </button>
            
            <div className="w-24 hidden sm:block">
              <div
                ref={volumeBarRef}
                className="h-1 bg-white/10 rounded-full cursor-pointer group relative"
                onClick={handleVolumeClick}
              >
                <div 
                  className="h-full bg-white rounded-full group-hover:bg-white/90 relative"
                  style={{ width: `${isVolumeDragging ? dragVolume : volume}%` }}
                >
                  <div 
                    className="absolute right-0 top-1/2 -translate-y-1/2 w-3 h-3 bg-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity cursor-grab active:cursor-grabbing shadow-lg"
                    onMouseDown={handleVolumeMouseDown}
                  />
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
