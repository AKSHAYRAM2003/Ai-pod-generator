'use client';

import React, { useState } from 'react';
import { Eye, EyeOff, Mail, User, AlertCircle, CheckCircle, X } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useUser } from '@/contexts/UserContext';

// --- HELPER COMPONENTS ---

const GoogleIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 48 48">
        <path fill="#FFC107" d="M43.611 20.083H42V20H24v8h11.303c-1.649 4.657-6.08 8-11.303 8-6.627 0-12-5.373-12-12s12-5.373 12-12c3.059 0 5.842 1.154 7.961 3.039l5.657-5.657C34.046 6.053 29.268 4 24 4 12.955 4 4 12.955 4 24s8.955 20 20 20 20-8.955 20-20c0-2.641-.21-5.236-.611-7.743z" />
        <path fill="#FF3D00" d="M6.306 14.691l6.571 4.819C14.655 15.108 18.961 12 24 12c3.059 0 5.842 1.154 7.961 3.039l5.657-5.657C34.046 6.053 29268 4 24 4 16.318 4 9.656 8.337 6.306 14.691z" />
        <path fill="#4CAF50" d="M24 44c5.166 0 9.86-1.977 13.409-5.192l-6.19-5.238C29.211 35.091 26.715 36 24 36c-5.202 0-9.619-3.317-11.283-7.946l-6.522 5.025C9.505 39.556 16.227 44 24 44z" />
        <path fill="#1976D2" d="M43.611 20.083H42V20H24v8h11.303c-.792 2.237-2.231 4.166-4.087 5.571l6.19 5.238C42.022 35.026 44 30.038 44 24c0-2.641-.21-5.236-.611-7.743z" />
    </svg>
);

// --- TYPE DEFINITIONS ---

export interface Testimonial {
  avatarSrc: string;
  name: string;
  handle: string;
  text: string;
}

interface SignUpFormData {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
}

interface SignUpStep {
  step: 'register' | 'verify';
  email?: string;
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

const SignUpPage: React.FC = () => {
  const router = useRouter();
  const { login } = useUser();
  const [showPassword, setShowPassword] = useState(false);
  const [currentStep, setCurrentStep] = useState<SignUpStep>({ step: 'register' });
  const [formData, setFormData] = useState<SignUpFormData>({
    email: '',
    password: '',
    first_name: '',
    last_name: ''
  });
  const [verificationCode, setVerificationCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  // Sample testimonials for the hero section
  const testimonials: Testimonial[] = [
    {
      avatarSrc: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&h=100&fit=crop&crop=face",
      name: "Alex Chen",
      handle: "@alexchen",
      text: "AI Pod Generator transformed how I create content. Amazing results!"
    },
    {
      avatarSrc: "https://images.unsplash.com/photo-1494790108755-2616b292b6cd?w=100&h=100&fit=crop&crop=face",
      name: "Sarah Wilson",
      handle: "@sarahw",
      text: "The quality of generated podcasts is incredible. Highly recommend!"
    }
  ];

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    // Clear field error when user starts typing
    if (fieldErrors[name]) {
      setFieldErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const handleSignUp = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setFieldErrors({});

    try {
      const response = await fetch('http://localhost:8000/api/v1/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (!response.ok) {
        if (data.detail?.error_code) {
          // Handle validation errors
          if (data.detail.error_code.includes('EMAIL')) {
            setFieldErrors(prev => ({ ...prev, email: data.detail.detail }));
          } else if (data.detail.error_code.includes('PASSWORD')) {
            setFieldErrors(prev => ({ ...prev, password: data.detail.detail }));
          } else {
            setError(data.detail.detail || 'Registration failed');
          }
        } else {
          setError(data.message || 'Registration failed');
        }
        return;
      }

      // Success - move to verification step
      setCurrentStep({ step: 'verify', email: formData.email });
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleVerification = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch('http://localhost:8000/api/v1/auth/verify-email', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ code: verificationCode }),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.detail?.detail || 'Verification failed');
        return;
      }

      // Success - store user data and redirect to home
      if (data.user) {
        login(data.user);
      }
      router.push('/');
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleSignUp = () => {
    // TODO: Implement Google OAuth
    console.log('Google sign up clicked');
  };

  const goToSignIn = () => {
    router.push('/signin');
  };

  const resendCode = async () => {
    setLoading(true);
    setError('');

    try {
      const response = await fetch('http://localhost:8000/api/v1/auth/resend-verification', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email: currentStep.email }),
      });

      if (response.ok) {
        setError(''); // Clear any previous errors
        // Maybe show a success message
      }
    } catch (err) {
      setError('Failed to resend code. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Registration form content
  const renderRegistrationForm = () => (
    <>
      <div>
        <h1 className="animate-element animate-delay-100 text-4xl md:text-5xl font-semibold leading-tight">
          <span className="font-light text-white tracking-tighter">Join AiPod</span>
        </h1>
      </div>
      <p className="animate-element animate-delay-200 text-muted-foreground">
        Create your account and start generating amazing podcasts with AI
      </p>

      {error && (
        <div className="animate-element animate-delay-250 flex items-center gap-2 p-4 rounded-2xl bg-red-500/10 border border-red-400/30 text-red-400">
          <AlertCircle className="w-5 h-5" />
          <span className="text-sm">{error}</span>
        </div>
      )}

      <form className="space-y-5" onSubmit={handleSignUp}>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="animate-element animate-delay-300">
            <label className="text-sm font-medium text-muted-foreground">First Name</label>
            <GlassInputWrapper error={!!fieldErrors.first_name}>
              <div className="relative">
                <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                <input
                  name="first_name"
                  type="text"
                  placeholder="Enter your first name"
                  value={formData.first_name}
                  onChange={handleInputChange}
                  className="w-full bg-transparent text-sm p-4 pl-12 rounded-2xl focus:outline-none"
                  required
                />
              </div>
            </GlassInputWrapper>
            {fieldErrors.first_name && <p className="text-red-400 text-xs mt-1">{fieldErrors.first_name}</p>}
          </div>

          <div className="animate-element animate-delay-350">
            <label className="text-sm font-medium text-muted-foreground">Last Name</label>
            <GlassInputWrapper error={!!fieldErrors.last_name}>
              <div className="relative">
                <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                <input
                  name="last_name"
                  type="text"
                  placeholder="Enter your last name"
                  value={formData.last_name}
                  onChange={handleInputChange}
                  className="w-full bg-transparent text-sm p-4 pl-12 rounded-2xl focus:outline-none"
                  required
                />
              </div>
            </GlassInputWrapper>
            {fieldErrors.last_name && <p className="text-red-400 text-xs mt-1">{fieldErrors.last_name}</p>}
          </div>
        </div>

        <div className="animate-element animate-delay-400">
          <label className="text-sm font-medium text-muted-foreground">Email Address</label>
          <GlassInputWrapper error={!!fieldErrors.email}>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-muted-foreground" />
              <input
                name="email"
                type="email"
                placeholder="Enter your email address"
                value={formData.email}
                onChange={handleInputChange}
                className="w-full bg-transparent text-sm p-4 pl-12 rounded-2xl focus:outline-none"
                required
              />
            </div>
          </GlassInputWrapper>
          {fieldErrors.email && <p className="text-red-400 text-xs mt-1">{fieldErrors.email}</p>}
        </div>

        <div className="animate-element animate-delay-500">
          <label className="text-sm font-medium text-muted-foreground">Password</label>
          <GlassInputWrapper error={!!fieldErrors.password}>
            <div className="relative">
              <input
                name="password"
                type={showPassword ? 'text' : 'password'}
                placeholder="Create a secure password"
                value={formData.password}
                onChange={handleInputChange}
                className="w-full bg-transparent text-sm p-4 pr-12 rounded-2xl focus:outline-none"
                required
                minLength={8}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute inset-y-0 right-3 flex items-center group"
              >
                {showPassword ? (
                  <EyeOff className="w-5 h-5 text-muted-foreground group-hover:text-neutral-700 transition-colors" />
                ) : (
                  <Eye className="w-5 h-5 text-muted-foreground group-hover:text-neutral-600 transition-colors" />
                )}
              </button>
            </div>
          </GlassInputWrapper>
          {fieldErrors.password && <p className="text-red-400 text-xs mt-1">{fieldErrors.password}</p>}
          <p className="text-xs text-muted-foreground mt-1">Must be at least 8 characters long</p>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="animate-element animate-delay-600 w-full rounded-full bg-gradient-to-t from-green-600 via-green-500 to-green-400 hover:from-green-700 hover:via-green-600 hover:to-green-500 text-white font-medium py-3 sm:py-4 px-6 sm:px-8 text-sm sm:text-base transition-all duration-200 shadow-sm hover:shadow-md hover:shadow-green-500/20 active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Creating Account...' : 'Create Account'}
        </button>
      </form>

      <div className="animate-element animate-delay-700 relative flex items-center justify-center">
        <span className="w-full border-t border-border"></span>
        <span className="px-4 text-sm text-muted-foreground rounded-full bg-background absolute">Or continue with</span>
      </div>

      <button
        onClick={handleGoogleSignUp}
        className="animate-element animate-delay-800 w-full flex items-center justify-center gap-3 border border-border rounded-full py-4 hover:bg-neutral-800/50 hover:border-neutral-600 transition-colors"
      >
        <GoogleIcon />
        Continue with Google
      </button>

      <p className="animate-element animate-delay-900 text-center text-sm text-muted-foreground">
        Already have an account?{' '}
        <button onClick={goToSignIn} className="text-white text-md hover:underline transition-colors">
          Sign In
        </button>
      </p>
    </>
  );

  // Verification form content
  const renderVerificationForm = () => (
    <>
      <div>
        <h1 className="animate-element animate-delay-100 text-4xl md:text-5xl font-semibold leading-tight">
          <span className="font-light text-white tracking-tighter">Check Your Email</span>
        </h1>
      </div>
      <p className="animate-element animate-delay-200 text-muted-foreground">
        We've sent a 6-digit verification code to <br />
        <span className="font-medium text-foreground">{currentStep.email}</span>
      </p>

      {error && (
        <div className="animate-element animate-delay-250 flex items-center gap-2 p-4 rounded-2xl bg-red-500/10 border border-red-400/30 text-red-400">
          <AlertCircle className="w-5 h-5" />
          <span className="text-sm">{error}</span>
        </div>
      )}

      <form className="space-y-5" onSubmit={handleVerification}>
        <div className="animate-element animate-delay-300">
          <label className="text-sm font-medium text-muted-foreground">Verification Code</label>
          <GlassInputWrapper>
            <input
              type="text"
              placeholder="Enter 6-digit code"
              value={verificationCode}
              onChange={(e) => setVerificationCode(e.target.value)}
              className="w-full bg-transparent text-sm p-4 rounded-2xl focus:outline-none text-center text-2xl tracking-[0.5em] font-mono"
              maxLength={6}
              pattern="[0-9]{6}"
              required
            />
          </GlassInputWrapper>
        </div>

        <button
          type="submit"
          disabled={loading || verificationCode.length !== 6}
          className="animate-element animate-delay-400 w-full rounded-full bg-gradient-to-t from-green-600 via-green-500 to-green-400 hover:from-green-700 hover:via-green-600 hover:to-green-500 text-white font-medium py-3 sm:py-4 px-6 sm:px-8 text-sm sm:text-base transition-all duration-200 shadow-sm hover:shadow-md hover:shadow-green-500/20 active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Verifying...' : 'Verify Email'}
        </button>
      </form>

      <div className="animate-element animate-delay-500 text-center">
        <p className="text-sm text-muted-foreground mb-2">Didn't receive the code?</p>
        <button
          onClick={resendCode}
          disabled={loading}
          className="text-green-400 hover:underline transition-colors text-sm disabled:opacity-50"
        >
          Resend Code
        </button>
      </div>

      <p className="animate-element animate-delay-600 text-center text-sm text-muted-foreground">
        Wrong email?{' '}
        <button
          onClick={() => setCurrentStep({ step: 'register' })}
          className="text-green-400 hover:underline transition-colors"
        >
          Go Back
        </button>
      </p>
    </>
  );

  return (
    <div className="h-[100dvh] flex flex-col md:flex-row font-geist w-[100dvw]">
      {/* Left column: sign-up form */}
      <section className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          <div className="flex flex-col gap-6">
            {currentStep.step === 'register' ? renderRegistrationForm() : renderVerificationForm()}
          </div>
        </div>
      </section>

      {/* Right column: hero image + testimonials */}
      <section className="hidden md:block flex-1 relative p-4">
        <div
          className="animate-slide-right animate-delay-300 absolute inset-4 rounded-3xl bg-cover bg-center"
          style={{
            backgroundImage: ` url('https://images.unsplash.com/photo-1590602847861-f357a9332bbc?w=800&h=1200&fit=crop')`
          }}
        ></div>
        {/* Close button positioned on the right image */}
        <button
          onClick={() => router.push('/')}
          className="absolute top-8 right-8 w-10 h-10 rounded-full bg-foreground/5 backdrop-blur-sm border border-white/10 hover:bg-foreground/10 hover:border-white/20 transition-all duration-200 flex items-center justify-center group z-10"
        >
          <X className="w-5 h-5 text-white/70 group-hover:text-white transition-colors" />
        </button>
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex gap-4 px-8 w-full justify-center">
          <TestimonialCard testimonial={testimonials[0]} delay="animate-delay-1000" />
          <div className="hidden xl:flex">
            <TestimonialCard testimonial={testimonials[1]} delay="animate-delay-1200" />
          </div>
        </div>
      </section>
    </div>
  );
};

export default SignUpPage;
