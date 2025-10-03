import NextAuth from 'next-auth'
import GoogleProvider from 'next-auth/providers/google'

const handler = NextAuth({
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    })
  ],
  callbacks: {
    async signIn({ user, account, profile }) {
      if (account?.provider === 'google') {
        try {
          // Send user data to your backend for registration/login
          const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/google-oauth`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              email: user.email,
              first_name: user.name?.split(' ')[0] || '',
              last_name: user.name?.split(' ').slice(1).join(' ') || '',
              google_id: user.id,
              avatar_url: user.image,
            }),
          })

          if (response.ok) {
            const data = await response.json()
            // Store backend tokens or user data if needed
            user.backendToken = data.access_token
            user.userData = data.user
            return true
          }
        } catch (error) {
          console.error('Backend OAuth error:', error)
        }
      }
      return true
    },
    async jwt({ token, user, account }) {
      if (account && user) {
        token.backendToken = (user as any).backendToken
        token.userData = (user as any).userData
      }
      return token
    },
    async session({ session, token }) {
      session.backendToken = token.backendToken as string
      session.userData = token.userData
      return session
    },
  },
  pages: {
    signIn: '/signin',
    error: '/auth/error',
  },
})

export { handler as GET, handler as POST }
