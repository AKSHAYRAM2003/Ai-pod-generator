'use client';

import { SignInPage } from "../../components/ui/sign-in";

export default function SignIn() {
  const testimonials = [
    {
      avatarSrc: "https://i.pinimg.com/1200x/88/c1/2c/88c12c0d8a371e1521fe89609d6785db.jpg",
      name: "Andrew",
      handle: "@andrew",
      text: "AI Pod Generator transformed how I create content. Amazing results!"
    },
    {
      avatarSrc: "https://i.pinimg.com/1200x/b3/60/0f/b3600f500d17fd6291bfa8dd16d773be.jpg",
      name: "williamson",
      handle: "@williamson",
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
