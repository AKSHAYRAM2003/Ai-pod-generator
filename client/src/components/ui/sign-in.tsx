'use client';

import React, { useState } from 'react';
import { Eye, EyeOff, AlertCircle, X } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useUser } from '@/contexts/UserContext';
import { signIn } from 'next-auth/react';
import Image from 'next/image';

// --- TYPE DEFINITIONS ---

export interface Testimonial {
  avatarSrc: string;
  name: string;
  handle: string;
  text: string;
}

interface SignInPageProps {
  title?: React.ReactNode;
  description?: React.ReactNode;
  heroImageSrc?: string;
  testimonials?: Testimonial[];
}

// --- SUB-COMPONENTS ---

const GlassInputWrapper = ({ children, error }: { children: React.ReactNode; error?: boolean }) => (
  <div className={`rounded-2xl border ${error ? 'border-red-400/70' : 'border-border'} bg-foreground/5 backdrop-blur-sm transition-colors focus-within:border-green-400/70 focus-within:bg-green-500/10`}>
    {children}
  </div>
);

const TestimonialCard = ({ testimonial, delay }: { testimonial: Testimonial, delay: string }) => (
  <div className={`animate-testimonial ${delay} flex items-start gap-3 rounded-3xl bg-card/40 dark:bg-zinc-800/40 backdrop-blur-xl border border-white/10 p-5 w-64`}>
    <img src={testimonial.avatarSrc} className="h-10 w-10 object-cover rounded-2xl" alt="avatar" />
    <div className="text-sm leading-snug">
      <p className="flex items-center gap-1 font-medium">{testimonial.name}</p>
      <p className="text-muted-foreground">{testimonial.handle}</p>
      <p className="mt-1 text-foreground/80">{testimonial.text}</p>
    </div>
  </div>
);

// --- MAIN COMPONENT ---

export const SignInPage: React.FC<SignInPageProps> = ({
  title = <span className="font-light text-white tracking-tighter">Welcome Back</span>,
  description = "Sign in to continue your journey with AI-powered podcasts",
  heroImageSrc,
  testimonials = [],
}) => {
  const router = useRouter();
  const { login } = useUser();
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    remember_me: false
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({ 
      ...prev, 
      [name]: type === 'checkbox' ? checked : value 
    }));
    // Clear field error when user starts typing
    if (fieldErrors[name]) {
      setFieldErrors(prev => ({ ...prev, [name]: '' }));
    }
    // Clear general error
    if (error) {
      setError('');
    }
  };

  const handleSignIn = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setLoading(true);
    setError('');
    setFieldErrors({});

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (!response.ok) {
        // Handle error response - extract the actual error message
        if (typeof data.detail === 'object' && data.detail !== null) {
          const errorMessage = data.detail.detail || 'Login failed';
          setError(errorMessage);
          
          // Map specific errors to fields if possible
          if (errorMessage.toLowerCase().includes('email')) {
            setFieldErrors({ email: errorMessage });
          } else if (errorMessage.toLowerCase().includes('password')) {
            setFieldErrors({ password: errorMessage });
          }
        } else if (typeof data.detail === 'string') {
          setError(data.detail);
        } else {
          setError(data.message || 'Login failed. Please check your credentials.');
        }
        setLoading(false);
        return;
      }

      // Success - store user data and access token
      if (data.user && data.access_token) {
        localStorage.setItem('token', data.access_token);
        if (data.refresh_token) {
          localStorage.setItem('refreshToken', data.refresh_token);
        }
        
        // Update user context
        await login(data.user);
        
        // Redirect to home
        router.push('/');
      }
    } catch (err) {
      console.error('Sign in error:', err);
      setError('Network error. Please check your connection and try again.');
      setLoading(false);
    }
  };

  const handleGoogleSignIn = async () => {
    setError('');
    setLoading(true);
    
    try {
      const result = await signIn('google', {
        callbackUrl: '/',
        redirect: false
      });
      
      if (result?.error) {
        setError('Google sign-in failed. Please try again.');
        setLoading(false);
      } else if (result?.url) {
        router.push(result.url);
      }
    } catch (err) {
      console.error('Google sign-in error:', err);
      setError('Google sign-in failed. Please try again.');
      setLoading(false);
    }
  };

  const handleResetPassword = () => {
    // TODO: Navigate to reset password page
    console.log('Reset password clicked');
    router.push('/reset-password');
  };

  const handleCreateAccount = () => {
    router.push('/signup');
  };

  return (
    <div className="h-[100dvh] flex flex-col md:flex-row font-geist w-[100dvw]">
      {/* Left column: sign-in form */}
      <section className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          <div className="flex flex-col gap-6">
            <div>
              <h1 className="animate-element animate-delay-100 text-4xl md:text-5xl font-semibold leading-tight">
                {title}
              </h1>
            </div>
            <p className="animate-element animate-delay-200 text-muted-foreground">{description}</p>

            {error && (
              <div className="animate-element animate-delay-250 flex items-center gap-2 p-4 rounded-2xl bg-red-500/10 border border-red-400/30 text-red-400">
                <AlertCircle className="w-5 h-5" />
                <span className="text-sm">{error}</span>
              </div>
            )}

            <form className="space-y-5" onSubmit={handleSignIn}>
              <div className="animate-element animate-delay-300">
                <label className="text-sm font-medium text-muted-foreground">Email Address</label>
                <GlassInputWrapper error={!!fieldErrors.email}>
                  <input 
                    name="email" 
                    type="email" 
                    value={formData.email}
                    onChange={handleInputChange}
                    placeholder="Enter your email address" 
                    className="w-full bg-transparent text-sm p-4 rounded-2xl focus:outline-none" 
                    required
                  />
                </GlassInputWrapper>
                {fieldErrors.email && (
                  <p className="text-xs text-red-400 mt-1">{fieldErrors.email}</p>
                )}
              </div>

              <div className="animate-element animate-delay-400">
                <label className="text-sm font-medium text-muted-foreground">Password</label>
                <GlassInputWrapper error={!!fieldErrors.password}>
                  <div className="relative">
                    <input 
                      name="password" 
                      type={showPassword ? 'text' : 'password'} 
                      value={formData.password}
                      onChange={handleInputChange}
                      placeholder="Enter your password" 
                      className="w-full bg-transparent text-sm p-4 pr-12 rounded-2xl focus:outline-none" 
                      required
                    />
                    <button 
                      type="button" 
                      onClick={() => setShowPassword(!showPassword)} 
                      className="absolute inset-y-0 right-3 flex items-center"
                    >
                      {showPassword ? (
                        <EyeOff className="w-5 h-5 text-muted-foreground hover:text-foreground transition-colors" />
                      ) : (
                        <Eye className="w-5 h-5 text-muted-foreground hover:text-foreground transition-colors" />
                      )}
                    </button>
                  </div>
                </GlassInputWrapper>
                {fieldErrors.password && (
                  <p className="text-xs text-red-400 mt-1">{fieldErrors.password}</p>
                )}
              </div>

              <div className="animate-element animate-delay-500 flex items-center justify-between text-sm">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input 
                    type="checkbox" 
                    name="remember_me" 
                    checked={formData.remember_me}
                    onChange={handleInputChange}
                    className="custom-checkbox" 
                  />
                  <span className="text-green-400">Keep me signed in</span>
                </label>
                <button
                  type="button"
                  onClick={handleResetPassword}
                  className="hover:underline text-green-400 transition-colors"
                >
                  Reset password
                </button>
              </div>

              <button 
                type="submit" 
                disabled={loading}
                className="animate-element animate-delay-600 w-full rounded-full bg-gradient-to-t from-green-600 via-green-500 to-green-400 hover:from-green-700 hover:via-green-600 hover:to-green-500 text-white font-medium py-3 sm:py-4 px-6 sm:px-8 text-sm sm:text-base transition-all duration-200 shadow-sm hover:shadow-md hover:shadow-green-500/20 active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Signing in...' : 'Sign In'}
              </button>
            </form>

            <div className="animate-element animate-delay-700 relative flex items-center justify-center">
              <span className="w-full border-t border-border"></span>
              <span className="px-4 text-sm text-muted-foreground rounded-full bg-background absolute">Or continue with</span>
            </div>

            <button 
              onClick={handleGoogleSignIn} 
              disabled={loading}
              className="animate-element animate-delay-800 w-full flex items-center justify-center gap-1 border border-border rounded-2xl py-4 hover:bg-neutral-800/50 hover:border-neutral-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Image
                src="/google-logo.png"
                alt="Google"
                width={18}
                height={18}
                className="rounded-none"
              />
              Continue with Google
            </button>

            <p className="animate-element animate-delay-900 text-center text-sm text-muted-foreground">
              New to our platform?{' '}
              <button 
                onClick={handleCreateAccount} 
                className="text-white text-md hover:underline transition-colors"
              >
                Create Account
              </button>
            </p>
          </div>
        </div>
      </section>

      {/* Right column: hero image + testimonials */}
      <section className="hidden md:block flex-1 relative p-4">
        <div 
          className="animate-slide-right animate-delay-300 absolute inset-4 rounded-3xl bg-cover bg-center" 
          style={{ 
            backgroundImage: heroImageSrc 
              ? `url(${heroImageSrc})` 
              : `url('https://images.unsplash.com/photo-1590602847861-f357a9332bbc?w=800&h=1200&fit=crop')` 
          }}
        ></div>
        {/* Close button positioned on the right image */}
        <button
          onClick={() => router.push('/')}
          className="absolute top-8 right-8 w-10 h-10 rounded-full bg-foreground/5 backdrop-blur-sm border border-white/10 hover:bg-foreground/10 hover:border-white/20 transition-all duration-200 flex items-center justify-center group z-10"
        >
          <X className="w-5 h-5 text-white/70 group-hover:text-white transition-colors" />
        </button>
        {testimonials.length > 0 && (
          <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex gap-4 px-8 w-full justify-center">
            <TestimonialCard testimonial={testimonials[0]} delay="animate-delay-1000" />
            {testimonials[1] && (
              <div className="hidden xl:flex">
                <TestimonialCard testimonial={testimonials[1]} delay="animate-delay-1200" />
              </div>
            )}
          </div>
        )}
      </section>
    </div>
  );
};  