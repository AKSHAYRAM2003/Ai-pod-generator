import NextAuth from 'next-auth'
import GoogleProvider from 'next-auth/providers/google'

const handler = NextAuth({
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    })
  ],
  pages: {
    signIn: '/signin',
    error: '/auth/error',
  },
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
            // Store backend data in user object
            Object.assign(user, {
              backendToken: data.access_token,
              refreshToken: data.refresh_token,
              userData: data.user,
              isNewUser: data.is_new_user
            })
            return true
          } else {
            console.error('Backend OAuth failed:', await response.text())
            return false
          }
        } catch (error) {
          console.error('Backend OAuth error:', error)
          return false
        }
      }
      return true
    },
    async jwt({ token, user, account }) {
      // Persist user data and tokens
      if (account && user) {
        token.backendToken = (user as any).backendToken
        token.refreshToken = (user as any).refreshToken
        token.userData = (user as any).userData
        token.isNewUser = (user as any).isNewUser
      }
      return token
    },
    async session({ session, token }) {
      // Send properties to the client
      Object.assign(session, {
        backendToken: token.backendToken,
        refreshToken: token.refreshToken,
        userData: token.userData,
        isNewUser: token.isNewUser
      })
      return session
    },
  },
})

export { handler as GET, handler as POST }
