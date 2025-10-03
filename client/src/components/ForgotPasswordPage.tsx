'use client';

import React, { useState } from 'react';
import { Eye, EyeOff, Mail, AlertCircle, CheckCircle, X, ArrowLeft } from 'lucide-react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';

// --- TYPE DEFINITIONS ---

export interface Testimonial {
  avatarSrc: string;
  name: string;
  handle: string;
  text: string;
}

interface ForgotPasswordStep {
  step: 'request' | 'verify' | 'success';
  email?: string;
}

// --- SUB-COMPONENTS ---

const GlassInputWrapper = ({ children, error }: { children: React.ReactNode; error?: boolean }) => (
  <div className={`rounded-2xl border ${error ? 'border-red-400/70' : 'border-border'} bg-foreground/5 backdrop-blur-sm transition-colors focus-within:border-green-400/70 focus-within:bg-green-500/10`}>
    {children}
  </div>
);

const TestimonialCard = ({ testimonial, delay }: { testimonial: Testimonial, delay: string }) => (
  <div className={`animate-testimonial ${delay} flex items-start gap-3 rounded-3xl bg-card/40 dark:bg-zinc-800/40 backdrop-blur-xl border border-white/10 p-5 w-full sm:w-64`}>
    <img src={testimonial.avatarSrc} className="h-10 w-10 object-cover rounded-full border border-gray-400" alt="avatar" />
    <div className="text-sm leading-snug">
      <p className="flex items-center gap-1 font-medium text-white">{testimonial.name}</p>
      <p className="text-black text-xs font-medium">{testimonial.handle}</p>
      <p className="mt-1 text-neutral-300">{testimonial.text}</p>
    </div>
  </div>
);

// --- MAIN COMPONENT ---

const ForgotPasswordPage: React.FC = () => {
  const router = useRouter();
  const [showPassword, setShowPassword] = useState(false);
  const [currentStep, setCurrentStep] = useState<ForgotPasswordStep>({ step: 'request' });
  const [email, setEmail] = useState('');
  const [code, setCode] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
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
      avatarSrc: "https://images.unsplash.com/photo-1605462863863-10d9e47e15ee?q=80&w=1740&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
      name: "Sarah Wilson",
      handle: "@sarahw",
      text: "The quality of generated podcasts is incredible. Highly recommend!"
    }
  ];

  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setEmail(e.target.value);
    if (fieldErrors.email) {
      setFieldErrors(prev => ({ ...prev, email: '' }));
    }
    if (error) setError('');
  };

  const handleCodeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value.replace(/\D/g, '').slice(0, 6);
    setCode(value);
    if (fieldErrors.code) {
      setFieldErrors(prev => ({ ...prev, code: '' }));
    }
    if (error) setError('');
  };

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setNewPassword(e.target.value);
    if (fieldErrors.password) {
      setFieldErrors(prev => ({ ...prev, password: '' }));
    }
    if (error) setError('');
  };

  const handleRequestReset = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setFieldErrors({});

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/password-reset/request`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      const data = await response.json();

      if (!response.ok) {
        const errorMessage = typeof data.detail === 'object' && data.detail !== null
          ? data.detail.detail || 'Failed to send reset code'
          : typeof data.detail === 'string'
          ? data.detail
          : data.message || 'Failed to send reset code';
        
        setError(errorMessage);
        setFieldErrors({ email: errorMessage });
        setLoading(false);
        return;
      }

      // Success - move to verify step
      setCurrentStep({ step: 'verify', email });
      setSuccess('Reset code sent to your email!');
      setTimeout(() => setSuccess(''), 3000);
      setLoading(false);
    } catch (err) {
      console.error('Request reset error:', err);
      setError('Network error. Please check your connection and try again.');
      setLoading(false);
    }
  };

  const handleVerifyAndReset = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setFieldErrors({});

    // Validate password on frontend
    if (newPassword.length < 8) {
      setFieldErrors({ password: 'Password must be at least 8 characters long' });
      setLoading(false);
      return;
    }

    const hasUpper = /[A-Z]/.test(newPassword);
    const hasLower = /[a-z]/.test(newPassword);
    const hasDigit = /[0-9]/.test(newPassword);

    if (!hasUpper || !hasLower || !hasDigit) {
      setFieldErrors({ password: 'Password must contain uppercase, lowercase, and number' });
      setLoading(false);
      return;
    }

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/password-reset/verify`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: currentStep.email,
          code,
          new_password: newPassword,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        const errorMessage = typeof data.detail === 'object' && data.detail !== null
          ? data.detail.detail || 'Failed to reset password'
          : typeof data.detail === 'string'
          ? data.detail
          : data.message || 'Failed to reset password';
        
        setError(errorMessage);
        
        // Map errors to fields
        if (errorMessage.toLowerCase().includes('code') || errorMessage.toLowerCase().includes('invalid')) {
          setFieldErrors({ code: errorMessage });
        } else if (errorMessage.toLowerCase().includes('password')) {
          setFieldErrors({ password: errorMessage });
        }
        
        setLoading(false);
        return;
      }

      // Success - move to success step
      setCurrentStep({ step: 'success' });
      setLoading(false);
    } catch (err) {
      console.error('Verify reset error:', err);
      setError('Network error. Please check your connection and try again.');
      setLoading(false);
    }
  };

  const resendCode = async () => {
    if (loading) return;
    
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/password-reset/request`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email: currentStep.email }),
      });

      if (!response.ok) {
        setError('Failed to resend code. Please try again.');
      } else {
        setSuccess('New code sent to your email!');
        setTimeout(() => setSuccess(''), 3000);
      }
    } catch (err) {
      setError('Failed to resend code. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const goToSignIn = () => {
    router.push('/signin');
  };

  // Request reset form content
  const renderRequestForm = () => (
    <>
      <div>
        <h1 className="animate-element animate-delay-100 text-4xl md:text-5xl font-semibold leading-tight">
          <span className="font-light text-white tracking-tighter">Forgot Password?</span>
        </h1>
      </div>
      <p className="animate-element animate-delay-200 text-neutral-500">
        No worries! Enter your email and we'll send you a reset code.
      </p>

      {error && (
        <div className="animate-element animate-delay-250 flex items-center gap-2 p-4 rounded-2xl bg-red-500/10 border border-red-400/30 text-red-400">
          <AlertCircle className="w-5 h-5" />
          <span className="text-sm">{error}</span>
        </div>
      )}

      {success && (
        <div className="animate-element animate-delay-250 flex items-center gap-2 p-4 rounded-2xl bg-green-500/10 border border-green-400/30 text-green-400">
          <CheckCircle className="w-5 h-5" />
          <span className="text-sm">{success}</span>
        </div>
      )}

      <form className="space-y-5" onSubmit={handleRequestReset}>
        <div className="animate-element animate-delay-300">
          <label className="text-sm font-medium text-muted-foreground">Email Address</label>
          <GlassInputWrapper error={!!fieldErrors.email}>
            <div className="relative">
              <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
              <input
                type="email"
                placeholder="Enter your registered email"
                value={email}
                onChange={handleEmailChange}
                className="w-full bg-transparent text-sm p-4 pl-12 rounded-2xl focus:outline-none"
                required
              />
            </div>
          </GlassInputWrapper>
          {fieldErrors.email && (
            <p className="text-xs text-red-400 mt-1">{fieldErrors.email}</p>
          )}
        </div>

        <button
          type="submit"
          disabled={loading}
          className="animate-element animate-delay-400 w-full rounded-full bg-gradient-to-t from-green-600 via-green-500 to-green-400 hover:from-green-700 hover:via-green-600 hover:to-green-500 text-white font-medium py-3 sm:py-4 px-6 sm:px-8 text-sm sm:text-base transition-all duration-200 shadow-sm hover:shadow-md hover:shadow-green-500/20 active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Sending Code...' : 'Send Reset Code'}
        </button>
      </form>

      <div className="animate-element animate-delay-500 flex items-center gap-2">
        <button
          onClick={goToSignIn}
          className="flex items-center gap-2 text-md text-neutral-400 hover:text-neutral-300 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Sign In
        </button>
      </div>
    </>
  );

  // Verify code and reset password form
  const renderVerifyForm = () => (
    <>
      <div>
        <h1 className="animate-element animate-delay-100 text-4xl md:text-5xl font-semibold leading-tight">
          <span className="font-light text-white tracking-tighter">Reset Your Password</span>
        </h1>
      </div>
      <p className="animate-element animate-delay-200 text-muted-foreground">
        We've sent a 6-digit code to <br />
        <span className="font-medium text-foreground">{currentStep.email}</span>
      </p>

      {error && (
        <div className="animate-element animate-delay-250 flex items-center gap-2 p-4 rounded-2xl bg-red-500/10 border border-red-400/30 text-red-400">
          <AlertCircle className="w-5 h-5" />
          <span className="text-sm">{error}</span>
        </div>
      )}

      {success && (
        <div className="animate-element animate-delay-250 flex items-center gap-2 p-4 rounded-2xl bg-green-500/10 border border-green-400/30 text-green-400">
          <CheckCircle className="w-5 h-5" />
          <span className="text-sm">{success}</span>
        </div>
      )}

      <form className="space-y-5" onSubmit={handleVerifyAndReset}>
        <div className="animate-element animate-delay-300">
          <label className="text-sm font-medium text-muted-foreground">Reset Code</label>
          <GlassInputWrapper error={!!fieldErrors.code}>
            <input
              type="text"
              placeholder="Enter 6-digit code"
              value={code}
              onChange={handleCodeChange}
              className="w-full bg-transparent text-sm p-4 rounded-2xl focus:outline-none text-center text-2xl tracking-[0.5em] font-mono"
              maxLength={6}
              pattern="[0-9]{6}"
              required
            />
          </GlassInputWrapper>
          {fieldErrors.code && (
            <p className="text-xs text-red-400 mt-1">{fieldErrors.code}</p>
          )}
        </div>

        <div className="animate-element animate-delay-400">
          <label className="text-sm font-medium text-muted-foreground">New Password</label>
          <GlassInputWrapper error={!!fieldErrors.password}>
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                placeholder="Enter your new password"
                value={newPassword}
                onChange={handlePasswordChange}
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
          <p className="text-xs text-muted-foreground mt-1">
            Must be at least 8 characters with uppercase, lowercase, and number
          </p>
        </div>

        <button
          type="submit"
          disabled={loading || code.length !== 6}
          className="animate-element animate-delay-500 w-full rounded-full bg-gradient-to-t from-green-600 via-green-500 to-green-400 hover:from-green-700 hover:via-green-600 hover:to-green-500 text-white font-medium py-3 sm:py-4 px-6 sm:px-8 text-sm sm:text-base transition-all duration-200 shadow-sm hover:shadow-md hover:shadow-green-500/20 active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Resetting Password...' : 'Reset Password'}
        </button>
      </form>

      <div className="animate-element animate-delay-600 text-center">
        <p className="text-sm text-muted-foreground mb-2">Didn't receive the code?</p>
        <button
          onClick={resendCode}
          disabled={loading}
          className="text-green-400 hover:underline transition-colors text-sm disabled:opacity-50"
        >
          Resend Code
        </button>
      </div>

      <p className="animate-element animate-delay-700 text-center text-sm text-muted-foreground">
        Wrong email?{' '}
        <button
          onClick={() => setCurrentStep({ step: 'request' })}
          className="text-green-400 hover:underline transition-colors"
        >
          Go Back
        </button>
      </p>
    </>
  );

  // Success message
  const renderSuccessMessage = () => (
    <>
      <div className="animate-element animate-delay-100 flex flex-col items-center gap-4">
        <div className="w-16 h-16 rounded-full bg-green-500/10 border border-green-400/30 flex items-center justify-center">
          <CheckCircle className="w-8 h-8 text-green-400" />
        </div>
        <h1 className="text-4xl md:text-5xl font-semibold leading-tight text-center">
          <span className="font-light text-white tracking-tighter">Password Reset!</span>
        </h1>
      </div>

      <p className="animate-element animate-delay-200 text-muted-foreground text-center">
        Your password has been successfully reset. <br />
        You can now sign in with your new password.
      </p>

      <button
        onClick={goToSignIn}
        className="animate-element animate-delay-300 w-full rounded-full bg-gradient-to-t from-green-600 via-green-500 to-green-400 hover:from-green-700 hover:via-green-600 hover:to-green-500 text-white font-medium py-3 sm:py-4 px-6 sm:px-8 text-sm sm:text-base transition-all duration-200 shadow-sm hover:shadow-md hover:shadow-green-500/20 active:scale-[0.98]"
      >
        Go to Sign In
      </button>
    </>
  );

  return (
    <div className="h-[100dvh] flex flex-col md:flex-row font-geist w-[100dvw] bg-neutral-900">
      {/* Left column: forgot password form */}
      <section className="flex-1 flex items-center justify-center p-4 sm:p-6 md:p-8 bg-neutral-900">
        <div className="w-full max-w-md">
          <div className="flex flex-col gap-6">
            {currentStep.step === 'request' && renderRequestForm()}
            {currentStep.step === 'verify' && renderVerifyForm()}
            {currentStep.step === 'success' && renderSuccessMessage()}
          </div>
        </div>
      </section>

      {/* Right column: hero image + testimonials */}
      <section className="hidden md:block flex-1 relative p-4">
        <div
          className="animate-slide-right animate-delay-300 absolute inset-4 rounded-3xl bg-cover bg-center"
          style={{
            backgroundImage: `url('https://i.pinimg.com/1200x/c3/40/69/c3406930b2541d98307aae2b57d1093a.jpg')`
          }}
        ></div>
        {/* Close button positioned on the right image */}
        <button
          onClick={() => router.push('/')}
          className="absolute top-8 right-8 w-10 h-10 rounded-full bg-foreground/5 backdrop-blur-sm border border-white/10 hover:bg-foreground/10 hover:border-white/20 transition-all duration-200 flex items-center justify-center group z-10"
        >
          <X className="w-5 h-5 text-white/70 group-hover:text-white transition-colors" />
        </button>
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col sm:flex-row gap-4 px-4 sm:px-8 w-full justify-center max-w-full overflow-x-auto">
          <TestimonialCard testimonial={testimonials[0]} delay="animate-delay-1000" />
          <div className="hidden xl:flex">
            <TestimonialCard testimonial={testimonials[1]} delay="animate-delay-1200" />
          </div>
        </div>
      </section>
    </div>
  );
};

export default ForgotPasswordPage;
