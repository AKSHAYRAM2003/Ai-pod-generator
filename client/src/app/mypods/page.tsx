'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Play, Pause, MoreVertical, Trash2, Globe, Share2, CheckCircle, Loader2, AlertCircle, Lock, LockOpen } from 'lucide-react';
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
  thumbnail_url?: string;
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
  const { playPodcast, currentPodcast, isPlaying, togglePlayPause } = useAudioPlayer();
  const [podcasts, setPodcasts] = useState<Podcast[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [pollingIds, setPollingIds] = useState<Set<string>>(new Set());
  const [justCompletedIds, setJustCompletedIds] = useState<Set<string>>(new Set());
  const [activeMenu, setActiveMenu] = useState<string | null>(null);

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

  const handleShare = async (podcast: Podcast) => {
    if (navigator.share && podcast.audio_url) {
      try {
        await navigator.share({
          title: podcast.topic,
          text: `Check out this AI-generated podcast: ${podcast.topic}`,
          url: window.location.origin + '/podcast/' + podcast.id,
        });
      } catch (err) {
        console.log('Error sharing:', err);
      }
    } else {
      // Fallback: copy link to clipboard
      const url = window.location.origin + '/podcast/' + podcast.id;
      navigator.clipboard.writeText(url);
      alert('Link copied to clipboard!');
    }
    setActiveMenu(null);
  };

  const toggleMenu = (podcastId: string) => {
    setActiveMenu(activeMenu === podcastId ? null : podcastId);
  };

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = () => setActiveMenu(null);
    if (activeMenu) {
      document.addEventListener('click', handleClickOutside);
      return () => document.removeEventListener('click', handleClickOutside);
    }
  }, [activeMenu]);

  // Group podcasts by status and category
  const generatingPodcasts = podcasts.filter(p => p.status === 'draft' || p.status === 'generating');
  const completedPodcasts = podcasts.filter(p => p.status === 'completed');
  const failedPodcasts = podcasts.filter(p => p.status === 'failed');
  
  // Get recent podcasts (3-4 most recent completed)
  const recentPodcasts = [...completedPodcasts]
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, 4);
  
  // Group completed podcasts by category
  const podcastsByCategory = completedPodcasts.reduce((acc, podcast) => {
    const categoryName = podcast.category?.name || 'Uncategorized';
    if (!acc[categoryName]) {
      acc[categoryName] = [];
    }
    acc[categoryName].push(podcast);
    return acc;
  }, {} as Record<string, Podcast[]>);

  // Render a podcast card
  const renderPodcastCard = (podcast: Podcast, showProgress = false) => {
    const isCurrentlyPlaying = currentPodcast?.id === podcast.id && isPlaying;
    const isGenerating = podcast.status === 'draft' || podcast.status === 'generating';

    return (
      <div
        key={podcast.id}
        className={`backdrop-blur-md bg-white/5 rounded-xl p-4 hover:bg-white/10 transition-all duration-300 group relative overflow-hidden
          ${isGenerating 
            ? 'border-2 bg-gradient-to-r from-blue-500/20 via-purple-500/20 to-pink-500/20 bg-[length:200%_200%] animate-shimmer' 
            : 'border border-white/10 hover:border-white/20'
          }
          ${justCompletedIds.has(podcast.id) ? 'ring-2 ring-green-500/50 animate-pulse' : ''}`}
      >
        <div className="flex items-start gap-4">
          {/* Thumbnail */}
          <div className={`w-20 h-20 rounded-lg flex items-center justify-center flex-shrink-0 overflow-hidden
            ${isGenerating 
              ? 'bg-gradient-to-br from-blue-500/30 via-purple-500/30 to-pink-500/30 animate-pulse' 
              : 'bg-gradient-to-br from-white/10 to-white/5 border border-white/10'
            }`}
          >
            {isGenerating ? (
              <Loader2 className="w-8 h-8 text-white animate-spin" />
            ) : podcast.thumbnail_url ? (
              <img 
                src={`http://localhost:8000${podcast.thumbnail_url}`} 
                alt={podcast.topic}
                className="w-full h-full object-cover"
              />
            ) : (
              <span className="text-3xl">{podcast.category?.icon || '🎙️'}</span>
            )}
          </div>

          {/* Content */}
          <div className="flex-1 min-w-0">
            {/* Title and Menu */}
            <div className="flex items-start justify-between gap-2 mb-2">
              <h3 className="text-white font-semibold text-base line-clamp-2 flex-1">
                {podcast.topic}
              </h3>
              
              {/* Three-dot menu for completed podcasts */}
              {podcast.status === 'completed' && (
                <div className="relative">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      toggleMenu(podcast.id);
                    }}
                    className="p-1.5 hover:bg-white/10 rounded-full transition-colors"
                  >
                    <MoreVertical className="w-4 h-4 text-gray-400" />
                  </button>
                  
                  {activeMenu === podcast.id && (
                    <div 
                      className="absolute right-0 top-8 bg-gray-900 border border-white/20 rounded-lg shadow-xl z-10 min-w-[160px]"
                      onClick={(e) => e.stopPropagation()}
                    >
                      <button
                        onClick={() => {
                          handlePublishToggle(podcast.id, podcast.is_public);
                          setActiveMenu(null);
                        }}
                        className="w-full px-4 py-2.5 text-left text-sm text-white hover:bg-white/10 flex items-center gap-2 first:rounded-t-lg"
                      >
                        {podcast.is_public ? (
                          <>
                            <Lock className="w-4 h-4" />
                            Make Private
                          </>
                        ) : (
                          <>
                            <LockOpen className="w-4 h-4" />
                            Make Public
                          </>
                        )}
                      </button>
                      <button
                        onClick={() => handleShare(podcast)}
                        className="w-full px-4 py-2.5 text-left text-sm text-white hover:bg-white/10 flex items-center gap-2"
                      >
                        <Share2 className="w-4 h-4" />
                        Share
                      </button>
                      <button
                        onClick={() => {
                          handleDelete(podcast.id);
                          setActiveMenu(null);
                        }}
                        className="w-full px-4 py-2.5 text-left text-sm text-red-400 hover:bg-red-500/10 flex items-center gap-2 last:rounded-b-lg border-t border-white/10"
                      >
                        <Trash2 className="w-4 h-4" />
                        Delete
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Metadata */}
            <div className="flex flex-wrap items-center gap-2 text-xs text-gray-400 mb-2">
              <span>{podcast.duration} min</span>
              <span>•</span>
              <span className="capitalize">
                {podcast.speaker_mode === 'single' ? 'Solo' : 'Conversation'}
              </span>
              {podcast.conversation_style && (
                <>
                  <span>•</span>
                  <span className="capitalize">{podcast.conversation_style}</span>
                </>
              )}
            </div>

            {/* Progress Bar for Generating */}
            {showProgress && isGenerating && (
              <div className="mb-3 space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-blue-400 font-medium">
                    {podcast.stage || 'Preparing...'}
                  </span>
                  <span className="text-white font-semibold">
                    {podcast.progress || 0}%
                  </span>
                </div>
                <div className="w-full h-2 bg-white/10 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 bg-[length:200%_200%] animate-shimmer transition-all duration-500 ease-out"
                    style={{ width: `${podcast.progress || 0}%` }}
                  />
                </div>
              </div>
            )}

            {/* Error Message */}
            {podcast.status === 'failed' && podcast.error_message && (
              <div className="mb-2 p-2 bg-red-500/10 border border-red-500/20 rounded text-xs text-red-400">
                {podcast.error_message}
              </div>
            )}

            {/* Success Message */}
            {justCompletedIds.has(podcast.id) && (
              <div className="mb-2 p-2 bg-green-500/10 border border-green-500/20 rounded text-xs text-green-400 flex items-center gap-1">
                <CheckCircle className="w-3 h-3" />
                Podcast generated successfully!
              </div>
            )}

            {/* Actions */}
            <div className="flex items-center gap-3 mt-2">
              {/* Play/Pause Button */}
              {podcast.status === 'completed' && podcast.audio_url && (
                <button
                  onClick={() => {
                    if (isCurrentlyPlaying) {
                      togglePlayPause();
                    } else {
                      playPodcast(podcast);
                    }
                  }}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium transition-all ${
                    isCurrentlyPlaying
                      ? 'bg-white text-black hover:bg-gray-200'
                      : 'bg-white/10 text-white hover:bg-white/20 border border-white/20'
                  }`}
                >
                  {isCurrentlyPlaying ? (
                    <>
                      <Pause className="w-3.5 h-3.5" />
                      Pause
                    </>
                  ) : (
                    <>
                      <Play className="w-3.5 h-3.5" />
                      Play
                    </>
                  )}
                </button>
              )}

              {/* Public Badge */}
              {podcast.is_public && podcast.status === 'completed' && (
                <span className="flex items-center gap-1 px-2 py-1 bg-green-500/10 text-green-400 border border-green-500/20 rounded text-xs">
                  <Globe className="w-3 h-3" />
                  Public
                </span>
              )}

              {/* Date */}
              <span className="text-xs text-gray-500 ml-auto">
                {formatDate(podcast.created_at)}
              </span>

              {/* Delete for failed/generating */}
              {(podcast.status === 'failed' || isGenerating) && (
                <button
                  onClick={() => handleDelete(podcast.id)}
                  className="p-1.5 text-red-400 hover:bg-red-500/10 rounded transition-colors"
                  title="Delete"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    );
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
        {/* Header */}
        <div className="mb-6 sm:mb-8">
          <h1 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold text-white mb-2">
            My Podcasts
          </h1>
          <p className="text-gray-400 text-sm sm:text-base md:text-lg">
            Your AI-generated podcasts • {podcasts.length} total
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

        {/* Generating Now Section */}
        {generatingPodcasts.length > 0 && (
          <section className="mb-8">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl sm:text-2xl font-bold text-white flex items-center gap-2">
                Generating Now
                <span className="px-2 py-0.5 bg-blue-500/20 text-blue-400 text-sm rounded-full">
                  {generatingPodcasts.length}
                </span>
              </h2>
            </div>
            
            <div className="grid grid-cols-1 gap-4">
              {generatingPodcasts.map(podcast => renderPodcastCard(podcast, true))}
            </div>
          </section>
        )}

        {/* Failed Podcasts Section */}
        {failedPodcasts.length > 0 && (
          <section className="mb-8">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl sm:text-2xl font-bold text-white flex items-center gap-2">
                Failed
                <span className="px-2 py-0.5 bg-red-500/20 text-red-400 text-sm rounded-full">
                  {failedPodcasts.length}
                </span>
              </h2>
            </div>
            
            <div className="grid grid-cols-1 gap-4">
              {failedPodcasts.map(podcast => renderPodcastCard(podcast, false))}
            </div>
          </section>
        )}

        {/* Recent Podcasts Section */}
        {recentPodcasts.length > 0 && (
          <section className="mb-8">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl sm:text-2xl font-bold text-white">Recent Podcasts</h2>
              {completedPodcasts.length > 4 && (
                <button 
                  onClick={() => router.push('/mypods?view=all')}
                  className="text-sm text-gray-400 hover:text-white transition-colors"
                >
                  See all
                </button>
              )}
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {recentPodcasts.map(podcast => renderPodcastCard(podcast, false))}
            </div>
          </section>
        )}

        {/* Podcasts by Category */}
        {Object.keys(podcastsByCategory).length > 0 && (
          <>
            {Object.entries(podcastsByCategory).map(([categoryName, categoryPodcasts]) => {
              // Skip if already shown in recent
              const uniquePodcasts = categoryPodcasts.filter(
                p => !recentPodcasts.some(rp => rp.id === p.id)
              ).slice(0, 4);

              if (uniquePodcasts.length === 0) return null;

              return (
                <section key={categoryName} className="mb-8">
                  <div className="flex items-center justify-between mb-6">
                    <h2 className="text-xl sm:text-2xl font-bold text-white">{categoryName}</h2>
                    {categoryPodcasts.length > 4 && (
                      <button 
                        onClick={() => router.push(`/mypods?category=${categoryName}`)}
                        className="text-sm text-gray-400 hover:text-white transition-colors"
                      >
                        See all
                      </button>
                    )}
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                    {uniquePodcasts.map(podcast => renderPodcastCard(podcast, false))}
                  </div>
                </section>
              );
            })}
          </>
        )}
      </main>
    </ProtectedRouteWrapper>
  );
}
