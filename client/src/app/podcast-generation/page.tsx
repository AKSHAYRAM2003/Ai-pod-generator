'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Sparkles, Clock, Users, MessageSquare, Mic, Loader2 } from 'lucide-react';
import ProtectedRouteWrapper from '@/components/ProtectedRouteWrapper';

interface Category {
  id: string;
  name: string;
  description: string;
  icon: string;
}

export default function PodcastGeneration() {
  const router = useRouter();
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingCategories, setLoadingCategories] = useState(true);
  const [error, setError] = useState('');

  // Form state
  const [formData, setFormData] = useState({
    topic: '',
    category_id: '',
    duration: 7,
    speaker_mode: 'two' as 'single' | 'two',
    voice_type: 'male' as 'male' | 'female',
    conversation_style: 'professional' as 'casual' | 'professional' | 'educational'
  });

  // Fetch categories on mount
  useEffect(() => {
    console.log('Component mounted, fetching categories...');
    fetchCategories();
  }, []);

  // Debug: Log state changes
  useEffect(() => {
    console.log('State update:', { loadingCategories, categoriesCount: categories.length, error });
  }, [loadingCategories, categories, error]);

  const fetchCategories = async () => {
    setLoadingCategories(true);
    try {
      console.log('Fetching categories from:', 'http://localhost:8000/api/v1/podcasts/categories/list');
      const response = await fetch('http://localhost:8000/api/v1/podcasts/categories/list');
      console.log('Response status:', response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log('Categories loaded:', data);
        if (Array.isArray(data) && data.length > 0) {
          setCategories(data);
          setError('');
        } else {
          console.warn('No categories returned from API');
          setError('No categories available');
        }
      } else {
        const errorText = await response.text();
        console.error('Failed to fetch categories:', response.status, errorText);
        setError(`Failed to load categories (Status: ${response.status})`);
      }
    } catch (err: any) {
      console.error('Error fetching categories:', err);
      setError(`Failed to load categories. ${err.message || 'Please check if the backend is running on port 8000.'}`);
    } finally {
      console.log('Setting loadingCategories to false');
      setLoadingCategories(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const token = localStorage.getItem('token');
      if (!token) {
        router.push('/signin');
        return;
      }

      const payload: any = {
        topic: formData.topic,
        category_id: formData.category_id,
        duration: formData.duration,
        speaker_mode: formData.speaker_mode,
      };

      // Add voice_type for single speaker
      if (formData.speaker_mode === 'single') {
        payload.voice_type = formData.voice_type;
      }

      // Add conversation_style for two speakers
      if (formData.speaker_mode === 'two') {
        payload.conversation_style = formData.conversation_style;
      }

      const response = await fetch('http://localhost:8000/api/v1/podcasts/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });

      const data = await response.json();

      if (response.ok) {
        // Success - redirect to My Pods
        router.push('/mypods');
      } else {
        // Handle error
        setError(data.detail || 'Failed to create podcast');
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  return (
    <ProtectedRouteWrapper>
      <main className="flex-1 bg-black p-4 sm:p-6 lg:p-8 overflow-y-auto">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center">
                <Sparkles className="w-6 h-6 text-black" />
              </div>
              <h1 className="text-3xl sm:text-4xl font-bold text-white">
                Generate Podcast
              </h1>
            </div>
            <p className="text-gray-400 text-base sm:text-lg">
              Create your AI-powered podcast in minutes
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Topic Input */}
            <div className="space-y-2">
              <label className="text-white font-medium text-sm flex items-center gap-2">
                <MessageSquare className="w-4 h-4" />
                Podcast Topic
              </label>
              <textarea
                value={formData.topic}
                onChange={(e) => handleInputChange('topic', e.target.value)}
                placeholder="e.g., The impact of artificial intelligence on modern healthcare"
                className="w-full bg-white/5 border border-white/10 rounded-lg p-4 text-white placeholder-gray-500 focus:outline-none focus:border-white/30 focus:bg-white/10 transition-all resize-none"
                rows={3}
                required
                minLength={5}
                maxLength={500}
              />
              <p className="text-gray-500 text-xs">
                {formData.topic.length}/500 characters
              </p>
            </div>

            {/* Category Selection */}
            <div className="space-y-2">
              <label className="text-white font-medium text-sm">
                Category
              </label>
              {loadingCategories ? (
                <div className="flex items-center justify-center p-8">
                  <Loader2 className="w-6 h-6 text-white animate-spin" />
                </div>
              ) : categories.length === 0 ? (
                <div className="p-8 text-center">
                  <p className="text-gray-400 mb-3">Failed to load categories</p>
                  <button
                    type="button"
                    onClick={fetchCategories}
                    className="px-4 py-2 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-colors text-sm"
                  >
                    Retry
                  </button>
                </div>
              ) : (
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
                  {categories.map((category) => (
                    <button
                      key={category.id}
                      type="button"
                      onClick={() => handleInputChange('category_id', category.id)}
                      className={`p-4 rounded-lg border transition-all ${
                        formData.category_id === category.id
                          ? 'bg-white/10 border-white/30 text-white'
                          : 'bg-white/5 border-white/10 text-gray-400 hover:bg-white/10 hover:border-white/20'
                      }`}
                    >
                      <div className="text-2xl mb-2">{category.icon}</div>
                      <div className="text-sm font-medium">{category.name}</div>
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Duration Selection */}
            <div className="space-y-2">
              <label className="text-white font-medium text-sm flex items-center gap-2">
                <Clock className="w-4 h-4" />
                Duration
              </label>
              <div className="grid grid-cols-3 gap-3">
                {[5, 7, 10].map((duration) => (
                  <button
                    key={duration}
                    type="button"
                    onClick={() => handleInputChange('duration', duration)}
                    className={`p-4 rounded-lg border transition-all ${
                      formData.duration === duration
                        ? 'bg-white/10 border-white/30 text-white'
                        : 'bg-white/5 border-white/10 text-gray-400 hover:bg-white/10 hover:border-white/20'
                    }`}
                  >
                    <div className="text-2xl font-bold">{duration}</div>
                    <div className="text-xs">minutes</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Speaker Mode */}
            <div className="space-y-2">
              <label className="text-white font-medium text-sm flex items-center gap-2">
                <Users className="w-4 h-4" />
                Speaker Mode
              </label>
              <div className="grid grid-cols-2 gap-3">
                <button
                  type="button"
                  onClick={() => handleInputChange('speaker_mode', 'single')}
                  className={`p-5 rounded-lg border transition-all ${
                    formData.speaker_mode === 'single'
                      ? 'bg-white/10 border-white/30 text-white'
                      : 'bg-white/5 border-white/10 text-gray-400 hover:bg-white/10 hover:border-white/20'
                  }`}
                >
                  <Mic className="w-6 h-6 mx-auto mb-2" />
                  <div className="font-medium">Single Speaker</div>
                  <div className="text-xs mt-1 text-gray-500">One voice narration</div>
                </button>
                <button
                  type="button"
                  onClick={() => handleInputChange('speaker_mode', 'two')}
                  className={`p-5 rounded-lg border transition-all ${
                    formData.speaker_mode === 'two'
                      ? 'bg-white/10 border-white/30 text-white'
                      : 'bg-white/5 border-white/10 text-gray-400 hover:bg-white/10 hover:border-white/20'
                  }`}
                >
                  <Users className="w-6 h-6 mx-auto mb-2" />
                  <div className="font-medium">Two Speakers</div>
                  <div className="text-xs mt-1 text-gray-500">Conversational format</div>
                </button>
              </div>
            </div>

            {/* Voice Type (for single speaker) */}
            {formData.speaker_mode === 'single' && (
              <div className="space-y-2">
                <label className="text-white font-medium text-sm">
                  Voice Type
                </label>
                <div className="grid grid-cols-2 gap-3">
                  {['male', 'female'].map((voice) => (
                    <button
                      key={voice}
                      type="button"
                      onClick={() => handleInputChange('voice_type', voice)}
                      className={`p-4 rounded-lg border transition-all capitalize ${
                        formData.voice_type === voice
                          ? 'bg-white/10 border-white/30 text-white'
                          : 'bg-white/5 border-white/10 text-gray-400 hover:bg-white/10 hover:border-white/20'
                      }`}
                    >
                      {voice}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Conversation Style (for two speakers) */}
            {formData.speaker_mode === 'two' && (
              <div className="space-y-2">
                <label className="text-white font-medium text-sm">
                  Conversation Style
                </label>
                <div className="grid grid-cols-3 gap-3">
                  {[
                    { value: 'casual', label: 'Casual', desc: 'Friendly chat' },
                    { value: 'professional', label: 'Professional', desc: 'Formal discussion' },
                    { value: 'educational', label: 'Educational', desc: 'Teaching format' }
                  ].map((style) => (
                    <button
                      key={style.value}
                      type="button"
                      onClick={() => handleInputChange('conversation_style', style.value)}
                      className={`p-4 rounded-lg border transition-all ${
                        formData.conversation_style === style.value
                          ? 'bg-white/10 border-white/30 text-white'
                          : 'bg-white/5 border-white/10 text-gray-400 hover:bg-white/10 hover:border-white/20'
                      }`}
                    >
                      <div className="font-medium text-sm">{style.label}</div>
                      <div className="text-xs mt-1 text-gray-500">{style.desc}</div>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Error Message */}
            {error && (
              <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
                <p className="text-red-400 text-sm">{error}</p>
              </div>
            )}

            {/* Submit Button */}
            <div className="flex gap-3 pt-4">
              <button
                type="button"
                onClick={() => router.back()}
                className="flex-1 px-6 py-3 bg-white/5 border border-white/10 text-white rounded-lg hover:bg-white/10 transition-all font-medium"
                disabled={loading}
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading || !formData.topic || !formData.category_id}
                className="flex-1 px-6 py-3 bg-white text-black rounded-lg hover:bg-gray-200 transition-all font-semibold disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5" />
                    Generate Podcast
                  </>
                )}
              </button>
            </div>
          </form>

          {/* Info Box */}
          <div className="mt-8 p-4 bg-white/5 border border-white/10 rounded-lg">
            <p className="text-gray-400 text-sm">
              <strong className="text-white">Note:</strong> Generation typically takes 2-5 minutes. 
              You can track the progress in your My Pods page. You're limited to 5 podcast generations per 24 hours.
            </p>
          </div>
        </div>
      </main>
    </ProtectedRouteWrapper>
  );
}
