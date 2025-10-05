'use client';

import React, { createContext, useContext, useState, useRef, useEffect } from 'react';

interface Podcast {
  id: string;
  topic: string;
  audio_url?: string;
  duration?: number;
  category?: {
    name: string;
    icon: string;
  };
}

interface AudioPlayerContextType {
  currentPodcast: Podcast | null;
  isPlaying: boolean;
  currentTime: number;
  duration: number;
  volume: number;
  playPodcast: (podcast: Podcast) => void;
  togglePlayPause: () => void;
  seek: (time: number) => void;
  setVolume: (volume: number) => void;
  audioElement: HTMLAudioElement | null;
}

const AudioPlayerContext = createContext<AudioPlayerContextType | null>(null);

export const useAudioPlayer = () => {
  const context = useContext(AudioPlayerContext);
  if (!context) {
    throw new Error('useAudioPlayer must be used within AudioPlayerProvider');
  }
  return context;
};

export const AudioPlayerProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currentPodcast, setCurrentPodcast] = useState<Podcast | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolumeState] = useState(65);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  // Initialize audio element
  useEffect(() => {
    if (!audioRef.current) {
      audioRef.current = new Audio();
      audioRef.current.volume = volume / 100;

      const audio = audioRef.current;

      // Event listeners
      const handleTimeUpdate = () => {
        setCurrentTime(audio.currentTime);
      };

      const handleDurationChange = () => {
        setDuration(audio.duration);
        console.log('Audio duration loaded:', audio.duration);
      };

      const handleEnded = () => {
        setIsPlaying(false);
        setCurrentTime(0);
      };

      const handlePlay = () => {
        setIsPlaying(true);
        console.log('Audio playing');
      };

      const handlePause = () => {
        setIsPlaying(false);
        console.log('Audio paused');
      };

      const handleError = (e: ErrorEvent) => {
        console.error('Audio error:', e);
        console.error('Audio error details:', {
          error: audio.error,
          code: audio.error?.code,
          message: audio.error?.message,
          src: audio.src
        });
        setIsPlaying(false);
      };

      const handleLoadStart = () => {
        console.log('Audio loading started');
      };

      const handleCanPlay = () => {
        console.log('Audio can play - ready to start');
      };

      audio.addEventListener('timeupdate', handleTimeUpdate);
      audio.addEventListener('durationchange', handleDurationChange);
      audio.addEventListener('ended', handleEnded);
      audio.addEventListener('play', handlePlay);
      audio.addEventListener('pause', handlePause);
      audio.addEventListener('error', handleError as any);
      audio.addEventListener('loadstart', handleLoadStart);
      audio.addEventListener('canplay', handleCanPlay);
    }

    return () => {
      if (audioRef.current) {
        const audio = audioRef.current;
        audio.pause();
        audio.src = '';
      }
    };
  }, []); // Empty dependency array - only run once

  const playPodcast = (podcast: Podcast) => {
    console.log('playPodcast called with:', podcast);
    
    if (!audioRef.current) {
      console.error('No audio element available');
      return;
    }
    
    if (!podcast.audio_url) {
      console.error('No audio URL provided for podcast');
      return;
    }

    // If same podcast, just toggle play/pause
    if (currentPodcast?.id === podcast.id) {
      console.log('Same podcast, toggling play/pause');
      togglePlayPause();
      return;
    }

    // Load new podcast
    setCurrentPodcast(podcast);
    const audioUrl = podcast.audio_url.startsWith('http') 
      ? podcast.audio_url 
      : `http://localhost:8000${podcast.audio_url}`;
    
    console.log('Loading podcast audio from URL:', audioUrl);
    console.log('Audio element state:', {
      readyState: audioRef.current.readyState,
      networkState: audioRef.current.networkState,
      currentSrc: audioRef.current.src
    });
    
    // Pause current audio first
    audioRef.current.pause();
    
    // Set new source
    audioRef.current.src = audioUrl;
    
    // Wait a bit for the source to be set, then play
    console.log('Attempting to play audio...');
    setTimeout(() => {
      if (audioRef.current) {
        audioRef.current.play()
          .then(() => {
            console.log('Audio playback started successfully');
          })
          .catch(error => {
            console.error('Error playing audio:', error);
            console.error('Error details:', {
              name: error.name,
              message: error.message,
              stack: error.stack
            });
            setIsPlaying(false);
          });
      }
    }, 100);
  };

  const togglePlayPause = () => {
    if (!audioRef.current) return;

    if (isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.play().catch(error => {
        console.error('Error playing audio:', error);
      });
    }
  };

  const seek = (time: number) => {
    if (!audioRef.current) return;
    audioRef.current.currentTime = time;
    setCurrentTime(time);
  };

  const setVolume = (newVolume: number) => {
    if (!audioRef.current) return;
    const vol = Math.max(0, Math.min(100, newVolume));
    setVolumeState(vol);
    audioRef.current.volume = vol / 100;
  };

  return (
    <AudioPlayerContext.Provider
      value={{
        currentPodcast,
        isPlaying,
        currentTime,
        duration,
        volume,
        playPodcast,
        togglePlayPause,
        seek,
        setVolume,
        audioElement: audioRef.current,
      }}
    >
      {children}
    </AudioPlayerContext.Provider>
  );
};
