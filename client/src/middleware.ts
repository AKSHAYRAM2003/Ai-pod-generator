import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl
  
  // Define protected routes
  const protectedRoutes = ['/profile', '/library', '/discover']
  
  // Check if current path is protected
  const isProtected = protectedRoutes.some(route => pathname.startsWith(route))
  
  if (isProtected) {
    // Check for authentication token in cookies or headers
    const token = request.cookies.get('next-auth.session-token')?.value || 
                  request.cookies.get('__Secure-next-auth.session-token')?.value
    
    // If no token, redirect to signin
    if (!token) {
      const url = new URL('/signin', request.url)
      url.searchParams.set('callbackUrl', pathname)
      return NextResponse.redirect(url)
    }
  }
  
  return NextResponse.next()
}

export const config = {
  matcher: [
    // Protected routes
    '/profile/:path*',
    '/library/:path*', 
    '/discover/:path*',
  ]
}
