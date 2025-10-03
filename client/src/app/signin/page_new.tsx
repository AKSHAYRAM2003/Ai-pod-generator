'use client';

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

  return (
    <SignInPage
      heroImageSrc="https://images.unsplash.com/photo-1590602847861-f357a9332bbc?w=800&h=1200&fit=crop"
      testimonials={testimonials}
    />
  );
}
