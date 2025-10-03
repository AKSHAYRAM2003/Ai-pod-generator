import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  // Since we're using client-side authentication with localStorage and ProtectedRouteWrapper,
  // we don't need server-side middleware protection
  // The ProtectedRouteWrapper component handles all authentication checks
  
  return NextResponse.next()
}

export const config = {
  matcher: [
    // No matchers needed - using client-side protection only
  ]
}
