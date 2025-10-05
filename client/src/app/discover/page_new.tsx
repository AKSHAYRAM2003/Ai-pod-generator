'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Play, Loader2, Search, Filter } from 'lucide-react';
import ProtectedRouteWrapper from '@/components/ProtectedRouteWrapper';

interface Category {
  id: string;
  name: string;
  description: string;
  icon: string;
}

interface Podcast {
  id: string;
  topic: string;
  duration: number;
  speaker_mode: string;
  conversation_style?: string;
  status: string;
  is_public: boolean;
  audio_url?: string;
  created_at: string;
  category?: {
    id: string;
    name: string;
    icon: string;
  };
}

export default function Discover() {
  const router = useRouter();
  const [categories, setCategories] = useState<Category[]>([]);
  const [podcasts, setPodcasts] = useState<Podcast[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    fetchCategories();
    fetchPublicPodcasts();
  }, [selectedCategory, page]);

  const fetchCategories = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/podcasts/categories/list');
      if (response.ok) {
        const data = await response.json();
        setCategories(data);
      }
    } catch (err) {
      console.error('Error fetching categories:', err);
    }
  };

  const fetchPublicPodcasts = async () => {
    try {
      setLoading(true);
      const categoryParam = selectedCategory ? `&category_id=${selectedCategory}` : '';
      const response = await fetch(
        `http://localhost:8000/api/v1/podcasts/discover?page=${page}&page_size=12${categoryParam}`
      );

      if (response.ok) {
        const data = await response.json();
        setPodcasts(data.podcasts);
        setTotalPages(data.total_pages);
      }
    } catch (err) {
      console.error('Error fetching podcasts:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    return date.toLocaleDateString();
  };

  const handleCategoryClick = (categoryId: string) => {
    if (selectedCategory === categoryId) {
      setSelectedCategory(null);
    } else {
      setSelectedCategory(categoryId);
    }
    setPage(1);
  };

  return (
    <ProtectedRouteWrapper>
      <main className="flex-1 bg-black p-4 sm:p-6 lg:p-8 overflow-y-auto">
        <div className="mb-6 sm:mb-8">
          <h1 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold text-white mb-2">
            Discover Podcasts
          </h1>
          <p className="text-gray-400 text-sm sm:text-base md:text-lg">
            Explore public AI-generated podcasts from the community.
          </p>
        </div>

        {/* Categories */}
        {categories.length > 0 && (
          <section className="mb-6 sm:mb-8">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl sm:text-2xl font-bold text-white">Browse by Category</h2>
              {selectedCategory && (
                <button
                  onClick={() => setSelectedCategory(null)}
                  className="text-sm text-gray-400 hover:text-white"
                >
                  Clear filter
                </button>
              )}
            </div>
            
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
              {categories.map((category) => (
                <button
                  key={category.id}
                  onClick={() => handleCategoryClick(category.id)}
                  className={`p-4 rounded-lg border transition-all ${
                    selectedCategory === category.id
                      ? 'bg-white/10 border-white/30'
                      : 'bg-white/5 border-white/10 hover:bg-white/10 hover:border-white/20'
                  }`}
                >
                  <div className="text-3xl mb-2">{category.icon}</div>
                  <div className="text-sm font-medium text-white">{category.name}</div>
                </button>
              ))}
            </div>
          </section>
        )}

        {/* Podcasts Grid */}
        <section>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl sm:text-2xl font-bold text-white">
              {selectedCategory ? 'Filtered Podcasts' : 'All Public Podcasts'}
            </h2>
            <div className="text-sm text-gray-400">
              {podcasts.length} podcast{podcasts.length !== 1 ? 's' : ''}
            </div>
          </div>

          {loading ? (
            <div className="flex items-center justify-center py-20">
              <Loader2 className="w-8 h-8 text-white animate-spin" />
            </div>
          ) : podcasts.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-20">
              <div className="w-20 h-20 bg-white/5 rounded-full flex items-center justify-center mb-4">
                <Search className="w-10 h-10 text-gray-400" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">No podcasts found</h3>
              <p className="text-gray-400 text-center max-w-md">
                {selectedCategory
                  ? 'No public podcasts in this category yet. Try selecting a different category.'
                  : 'No public podcasts available yet. Be the first to create and publish one!'}
              </p>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {podcasts.map((podcast) => (
                  <div
                    key={podcast.id}
                    className="backdrop-blur-md bg-white/5 border border-white/10 rounded-xl p-5 hover:bg-white/10 hover:border-white/20 transition-all duration-300 cursor-pointer group"
                  >
                    {/* Category Icon */}
                    <div className="w-16 h-16 bg-gradient-to-br from-white/10 to-white/5 rounded-xl flex items-center justify-center mb-4 text-3xl border border-white/10">
                      {podcast.category?.icon || '🎙️'}
                    </div>

                    {/* Topic */}
                    <h3 className="text-white font-semibold text-lg mb-2 line-clamp-2 group-hover:underline">
                      {podcast.topic}
                    </h3>

                    {/* Metadata */}
                    <div className="flex flex-wrap items-center gap-2 text-sm text-gray-400 mb-3">
                      {podcast.category && (
                        <span className="text-gray-300">{podcast.category.name}</span>
                      )}
                      <span>•</span>
                      <span>{podcast.duration} min</span>
                      {podcast.conversation_style && (
                        <>
                          <span>•</span>
                          <span className="capitalize">{podcast.conversation_style}</span>
                        </>
                      )}
                    </div>

                    {/* Date */}
                    <div className="text-xs text-gray-500 mb-4">
                      {formatDate(podcast.created_at)}
                    </div>

                    {/* Play Button */}
                    {podcast.audio_url && (
                      <button className="w-full px-4 py-2 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-colors flex items-center justify-center gap-2">
                        <Play className="w-4 h-4" />
                        Play Podcast
                      </button>
                    )}
                  </div>
                ))}
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex items-center justify-center gap-2 mt-8">
                  <button
                    onClick={() => setPage(p => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className="px-4 py-2 bg-white/5 border border-white/10 text-white rounded-lg hover:bg-white/10 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Previous
                  </button>
                  <span className="text-gray-400 px-4">
                    Page {page} of {totalPages}
                  </span>
                  <button
                    onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                    disabled={page === totalPages}
                    className="px-4 py-2 bg-white/5 border border-white/10 text-white rounded-lg hover:bg-white/10 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Next
                  </button>
                </div>
              )}
            </>
          )}
        </section>
      </main>
    </ProtectedRouteWrapper>
  );
}
