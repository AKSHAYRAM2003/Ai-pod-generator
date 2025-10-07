'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Play, Pause, MoreVertical, Trash2, Globe, Share2, CheckCircle } from 'lucide-react';
import ProtectedRouteWrapper from '@/components/ProtectedRouteWrapper';
import { useAudioPlayer } from '@/contexts/AudioPlayerContext';

interface Podcast {
  id: string;
  topic: string;
  duration: number;
  speaker_mode: string;
  voice_type?: string;
  conversation_style?: string;
  status: 'draft' | 'generating' | 'completed' | 'failed';
  is_public: boolean;
  audio_url?: string;
  error_message?: string;
  created_at: string;
  progress?: number;
  stage?: string;
  category?: {
    id: string;
    name: string;
    icon: string;
  };
}

export default function MyPods() {
  const router = useRouter();
  const { playPodcast, currentPodcast, isPlaying } = useAudioPlayer();
  const [podcasts, setPodcasts] = useState<Podcast[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [pollingIds, setPollingIds] = useState<Set<string>>(new Set());
  const [justCompletedIds, setJustCompletedIds] = useState<Set<string>>(new Set());

  useEffect(() => {
    fetchMyPodcasts();
    // Set up polling interval for processing podcasts
    const interval = setInterval(() => {
      checkProcessingPodcasts();
    }, 5000); // Poll every 5 seconds

    return () => clearInterval(interval);
  }, []);

  const fetchMyPodcasts = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        router.push('/signin');
        return;
      }

      const response = await fetch('http://localhost:8000/api/v1/podcasts/my-podcasts?page=1&page_size=50', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        console.log('[MyPods] Fetched podcasts:', data.podcasts);
        setPodcasts(data.podcasts);
        
        // Start polling for processing podcasts (including draft and generating)
        const processingPods = data.podcasts.filter(
          (p: Podcast) => p.status === 'draft' || p.status === 'generating'
        );
        console.log('[MyPods] Starting polling for:', processingPods.map((p: Podcast) => ({ id: p.id, status: p.status })));
        setPollingIds(new Set(processingPods.map((p: Podcast) => p.id)));
      } else if (response.status === 401) {
        router.push('/signin');
      } else {
        setError('Failed to load podcasts');
      }
    } catch (err) {
      setError('An error occurred while loading podcasts');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const checkProcessingPodcasts = async () => {
    const token = localStorage.getItem('token');
    if (!token || pollingIds.size === 0) return;

    // Check status for each processing podcast
    for (const podcastId of pollingIds) {
      try {
        const response = await fetch(
          `http://localhost:8000/api/v1/podcasts/${podcastId}/status`,
          {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          }
        );

        if (response.ok) {
          const statusData = await response.json();
          console.log(`[MyPods] Status update for ${podcastId}:`, statusData);
          
          // Check if podcast just completed
          const wasGenerating = podcasts.find(p => p.id === podcastId)?.status === 'generating';
          const isNowCompleted = statusData.status === 'completed';
          
          // Update podcast in the list with progress and stage
          setPodcasts(prev => prev.map(p => 
            p.id === podcastId 
              ? { 
                  ...p, 
                  status: statusData.status, 
                  audio_url: statusData.audio_url, 
                  error_message: statusData.error_message,
                  progress: statusData.progress,
                  stage: statusData.stage
                }
              : p
          ));

          // Stop polling if completed or failed
          if (statusData.status === 'completed' || statusData.status === 'failed') {
            console.log(`[MyPods] Stopping poll for ${podcastId} - status: ${statusData.status}, audio_url: ${statusData.audio_url}`);
            
            // Mark as just completed for animation
            if (wasGenerating && isNowCompleted) {
              setJustCompletedIds(prev => new Set(prev).add(podcastId));
              // Remove from just completed after 10 seconds
              setTimeout(() => {
                setJustCompletedIds(prev => {
                  const newSet = new Set(prev);
                  newSet.delete(podcastId);
                  return newSet;
                });
              }, 10000);
            }
            
            setPollingIds(prev => {
              const newSet = new Set(prev);
              newSet.delete(podcastId);
              return newSet;
            });
          }
        }
      } catch (err) {
        console.error(`Error checking status for podcast ${podcastId}:`, err);
      }
    }
  };

  const handlePublishToggle = async (podcastId: string, currentStatus: boolean) => {
    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      const response = await fetch(
        `http://localhost:8000/api/v1/podcasts/${podcastId}/publish`,
        {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({ is_public: !currentStatus })
        }
      );

      if (response.ok) {
        setPodcasts(prev => prev.map(p => 
          p.id === podcastId ? { ...p, is_public: !currentStatus } : p
        ));
      }
    } catch (err) {
      console.error('Error toggling publish status:', err);
    }
  };

  const handleDelete = async (podcastId: string) => {
    if (!confirm('Are you sure you want to delete this podcast?')) return;

    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      const response = await fetch(
        `http://localhost:8000/api/v1/podcasts/${podcastId}`,
        {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (response.ok || response.status === 204) {
        setPodcasts(prev => prev.filter(p => p.id !== podcastId));
      }
    } catch (err) {
      console.error('Error deleting podcast:', err);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'draft':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 bg-gray-500/10 text-gray-400 border border-gray-500/20 rounded text-xs">
            <Loader2 className="w-3 h-3 animate-spin" />
            Queued
          </span>
        );
      case 'generating':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 bg-blue-500/10 text-blue-400 border border-blue-500/20 rounded text-xs">
            <Loader2 className="w-3 h-3 animate-spin" />
            Generating
          </span>
        );
      case 'completed':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 bg-green-500/10 text-green-400 border border-green-500/20 rounded text-xs">
            <CheckCircle className="w-3 h-3" />
            Completed
          </span>
        );
      case 'failed':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 bg-red-500/10 text-red-400 border border-red-500/20 rounded text-xs">
            <AlertCircle className="w-3 h-3" />
            Failed
          </span>
        );
      default:
        return null;
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} min ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    return date.toLocaleDateString();
  };

  if (loading) {
    return (
      <ProtectedRouteWrapper>
        <main className="flex-1 bg-black p-4 sm:p-6 lg:p-8 overflow-y-auto flex items-center justify-center">
          <Loader2 className="w-8 h-8 text-white animate-spin" />
        </main>
      </ProtectedRouteWrapper>
    );
  }

  return (
    <ProtectedRouteWrapper>
      <main className="flex-1 bg-black p-4 sm:p-6 lg:p-8 overflow-y-auto">
        <div className="mb-6 sm:mb-8">
          <h1 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold text-white mb-2">
            My Pods
          </h1>
          <p className="text-gray-400 text-sm sm:text-base md:text-lg">
            Your AI-generated podcasts ({podcasts.length} total)
          </p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
            <p className="text-red-400">{error}</p>
          </div>
        )}

        {/* Empty State */}
        {podcasts.length === 0 && (
          <div className="flex flex-col items-center justify-center py-20">
            <div className="w-20 h-20 bg-white/5 rounded-full flex items-center justify-center mb-4">
              <Play className="w-10 h-10 text-gray-400" />
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">No podcasts yet</h3>
            <p className="text-gray-400 mb-6 text-center max-w-md">
              Start generating your first AI-powered podcast. Click the button below to get started.
            </p>
            <button
              onClick={() => router.push('/podcast-generation')}
              className="px-6 py-3 bg-white text-black rounded-full font-semibold hover:bg-gray-200 transition-colors"
            >
              Generate Your First Podcast
            </button>
          </div>
        )}

        {/* Podcasts Grid */}
        {podcasts.length > 0 && (
          <div className="grid grid-cols-1 gap-4">
            {podcasts.map((podcast) => (
              <div
                key={podcast.id}
                className="backdrop-blur-md bg-white/5 border border-white/10 rounded-xl p-5 hover:bg-white/10 hover:border-white/20 transition-all duration-300 group"
              >
                <div className="flex items-start gap-4">
                  {/* Icon/Category */}
                  <div className="w-16 h-16 bg-gradient-to-br from-white/10 to-white/5 rounded-xl flex items-center justify-center flex-shrink-0 text-3xl border border-white/10">
                    {podcast.category?.icon || '🎙️'}
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-3 mb-2">
                      <div className="flex-1">
                        <h3 className="text-white font-semibold text-lg mb-1 line-clamp-2">
                          {podcast.topic}
                        </h3>
                        <div className="flex flex-wrap items-center gap-2 text-sm text-gray-400">
                          {podcast.category && (
                            <span className="text-gray-300">{podcast.category.name}</span>
                          )}
                          <span>•</span>
                          <span>{podcast.duration} min</span>
                          <span>•</span>
                          <span className="capitalize">{podcast.speaker_mode} speaker{podcast.speaker_mode === 'two' ? 's' : ''}</span>
                          {podcast.conversation_style && (
                            <>
                              <span>•</span>
                              <span className="capitalize">{podcast.conversation_style}</span>
                            </>
                          )}
                        </div>
                      </div>
                      {getStatusBadge(podcast.status)}
                    </div>

                    {/* Error Message */}
                    {podcast.status === 'failed' && podcast.error_message && (
                      <div className="mb-3 p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
                        <p className="text-red-400 text-sm">{podcast.error_message}</p>
                      </div>
                    )}

                    {/* Progress Bar for Generating Podcasts */}
                    {(podcast.status === 'draft' || podcast.status === 'generating') && (
                      <div className="mb-3 space-y-2">
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-gray-400">
                            {podcast.stage || 'Preparing...'}
                          </span>
                          <span className="text-white font-semibold">
                            {podcast.progress || 0}%
                          </span>
                        </div>
                        <div className="w-full h-2 bg-white/10 rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all duration-500 ease-out"
                            style={{ width: `${podcast.progress || 0}%` }}
                          />
                        </div>
                      </div>
                    )}

                    {/* Success Message when Completed */}
                    {podcast.status === 'completed' && podcast.audio_url && justCompletedIds.has(podcast.id) && (
                      <div className="mb-3 p-3 bg-green-500/10 border border-green-500/20 rounded-lg animate-pulse">
                        <p className="text-green-400 text-sm font-semibold flex items-center gap-2">
                          <CheckCircle className="w-4 h-4" />
                          Your podcast generated successfully! Ready to play.
                        </p>
                      </div>
                    )}

                    {/* Actions */}
                    <div className="flex flex-wrap items-center gap-3 mt-3">
                      <span className="text-xs text-gray-500">{formatDate(podcast.created_at)}</span>
                      
                      {podcast.status === 'completed' && podcast.audio_url && (
                        <>
                          <button
                            onClick={() => playPodcast(podcast)}
                            className={`text-sm px-3 py-1.5 rounded-lg transition-colors flex items-center gap-1 ${
                              currentPodcast?.id === podcast.id && isPlaying
                                ? 'bg-white text-black'
                                : 'bg-white/10 text-white hover:bg-white/20'
                            }`}
                          >
                            <Play className="w-3 h-3" />
                            {currentPodcast?.id === podcast.id && isPlaying ? 'Playing' : 'Play'}
                          </button>
                          
                          <button
                            onClick={() => handlePublishToggle(podcast.id, podcast.is_public)}
                            className={`text-sm px-3 py-1.5 rounded-lg transition-colors ${
                              podcast.is_public
                                ? 'bg-green-500/10 text-green-400 border border-green-500/20 hover:bg-green-500/20'
                                : 'bg-white/10 text-white hover:bg-white/20'
                            }`}
                          >
                            {podcast.is_public ? 'Public' : 'Make Public'}
                          </button>
                        </>
                      )}

                      <button
                        onClick={() => handleDelete(podcast.id)}
                        className="text-sm px-3 py-1.5 bg-red-500/10 text-red-400 border border-red-500/20 rounded-lg hover:bg-red-500/20 transition-colors ml-auto"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Refresh Button */}
        {podcasts.length > 0 && (
          <div className="mt-6 flex justify-center">
            <button
              onClick={fetchMyPodcasts}
              className="px-4 py-2 bg-white/5 border border-white/10 text-white rounded-lg hover:bg-white/10 transition-colors flex items-center gap-2"
            >
              <RefreshCw className="w-4 h-4" />
              Refresh
            </button>
          </div>
        )}
      </main>
    </ProtectedRouteWrapper>
  );
}
