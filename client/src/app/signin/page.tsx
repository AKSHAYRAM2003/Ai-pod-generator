import { SignInPage } from "../../components/ui/sign-in";

export default function SignIn() {
  const testimonials = [
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

  const handleSignIn = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    // TODO: Implement sign-in logic
    console.log('Sign in submitted');
  };

  const handleGoogleSignIn = () => {
    // TODO: Implement Google OAuth
    console.log('Google sign in clicked');
  };

  const handleResetPassword = () => {
    // TODO: Navigate to reset password page
    console.log('Reset password clicked');
  };

  const handleCreateAccount = () => {
    // Navigate to signup page
    window.location.href = '/signup';
  };

  return (
    <SignInPage
      heroImageSrc="https://images.unsplash.com/photo-1590602847861-f357a9332bbc?w=800&h=1200&fit=crop"
      testimonials={testimonials}
      onSignIn={handleSignIn}
      onGoogleSignIn={handleGoogleSignIn}
      onResetPassword={handleResetPassword}
      onCreateAccount={handleCreateAccount}
    />
  );
}
