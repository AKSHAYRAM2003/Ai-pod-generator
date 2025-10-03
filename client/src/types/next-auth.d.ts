import { DefaultSession, DefaultUser } from 'next-auth'
import { JWT, DefaultJWT } from 'next-auth/jwt'

declare module 'next-auth' {
  interface Session extends DefaultSession {
    backendToken?: string
    userData?: any
  }

  interface User extends DefaultUser {
    backendToken?: string
    userData?: any
  }
}

declare module 'next-auth/jwt' {
  interface JWT extends DefaultJWT {
    backendToken?: string
    userData?: any
  }
}
