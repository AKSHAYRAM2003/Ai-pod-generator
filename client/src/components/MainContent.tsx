export default function MainContent() {
  const featuredPodcasts = [
    {
      title: "The Future of AI",
      author: "By SynthCast",
      color: "bg-gradient-to-br from-pink-200 to-pink-300"
    },
    {
      title: "Digital Minds",
      author: "By NeuralNet Radio",
      color: "bg-gradient-to-br from-teal-200 to-teal-300"
    },
    {
      title: "Tech Unfiltered",
      author: "By Code & Coffee",
      color: "bg-gradient-to-br from-amber-200 to-amber-300"
    },
    {
      title: "Innovation Wave",
      author: "By Visionary Voices",
      color: "bg-gradient-to-br from-orange-200 to-orange-300"
    },
    {
      title: "Creator's Corner",
      author: "By The Podcasters",
      color: "bg-gradient-to-br from-orange-300 to-orange-400"
    },
    {
      title: "Tech Unfiltered",
      author: "By Code & Coffee",
      color: "bg-gradient-to-br from-amber-200 to-amber-300"
    }
  ];

  const trendingEpisodes = [
    {
      title: "The Rise of Generative Audio",
      podcast: "The Future of AI",
      avatar: "bg-gradient-to-br from-blue-400 to-blue-600",
      profileImage: "/api/placeholder/80/80"
    },
    {
      title: "Ethics in Machine Learning",
      podcast: "Digital Minds",
      avatar: "bg-gradient-to-br from-green-400 to-green-600",
      profileImage: "/api/placeholder/80/80"
    },
    {
      title: "Latest AI Breakthroughs", 
      podcast: "Tech Unfiltered",
      avatar: "bg-gradient-to-br from-purple-400 to-purple-600",
      profileImage: "/api/placeholder/80/80"
    },
    {
      title: "Future of Quantum Computing",
      podcast: "Science Today",
      avatar: "bg-gradient-to-br from-red-400 to-red-600",
      profileImage: "/api/placeholder/80/80"
    },
    {
      title: "AI in Healthcare Revolution",
      podcast: "Medical Tech Talk",
      avatar: "bg-gradient-to-br from-indigo-400 to-indigo-600",
      profileImage: "/api/placeholder/80/80"
    },{
      title: "Future of Quantum Computing",
      podcast: "Science Today",
      avatar: "bg-gradient-to-br from-red-400 to-red-600",
      profileImage: "/api/placeholder/80/80"
    },
  ];

  const newReleases = [
    {
      title: "Revolutionary AI Chatbots",
      podcast: "Tech Tomorrow",
      avatar: "bg-gradient-to-br from-cyan-400 to-blue-500"
    },
    {
      title: "Machine Learning Basics",
      podcast: "Code Academy",
      avatar: "bg-gradient-to-br from-emerald-400 to-green-500"
    },
    {
      title: "Blockchain Explained Simply",
      podcast: "Crypto Insights",
      avatar: "bg-gradient-to-br from-orange-400 to-red-500"
    },
    {
      title: "Virtual Reality Future",
      podcast: "Digital Horizons",
      avatar: "bg-gradient-to-br from-purple-400 to-pink-500"
    },
    {
      title: "Cybersecurity Today",
      podcast: "Security First",
      avatar: "bg-gradient-to-br from-yellow-400 to-orange-500"
    },
    {
      title: "Data Analytics Deep Dive",
      podcast: "Numbers Matter",
      avatar: "bg-gradient-to-br from-indigo-400 to-purple-500"
    }
  ];

  return (
    <main className="flex-1 bg-black p-4 sm:p-6 lg:p-8 overflow-y-auto">
      {/* Welcome Section */}
      <div className="mb-6 sm:mb-8">
        <h1 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold text-white mb-2">
          Welcome to AI Podcast Generator
        </h1>
        <p className="text-gray-400 text-sm sm:text-base md:text-lg">
          Your hub for creating and discovering AI-powered audio.
        </p>
      </div>

      {/* New Releases */}
      <section className="mb-6 sm:mb-8">
        <div className="flex items-center justify-between mb-4 sm:mb-6">
          <h2 className="text-xl sm:text-2xl font-bold text-white">New Releases</h2>
          <button className="text-sm sm:text-base text-gray-400 hover:text-white transition-colors">
            See all
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {newReleases.map((release, index) => (
            <div
              key={index}
              className="backdrop-blur-md bg-white/10 border border-white/20 rounded-xl p-4 hover:bg-white/15 hover:border-white/30 transition-all duration-300 cursor-pointer group shadow-lg hover:shadow-xl hover:shadow-white/10"
            >
              <div className="flex items-center space-x-4">
                {/* Profile Image */}
                <div className={`w-16 h-16 ${release.avatar} rounded-xl flex items-center justify-center flex-shrink-0 overflow-hidden shadow-md`}>
                  <div className="w-10 h-10 bg-white/30 rounded-lg flex items-center justify-center backdrop-blur-sm">
                    <div className="w-6 h-6 bg-white/50 rounded-md"></div>
                  </div>
                </div>
                
                {/* Release Info */}
                <div className="flex-1 min-w-0">
                  <h3 className="text-white font-semibold mb-1 group-hover:underline text-base line-clamp-2 leading-tight drop-shadow-sm">
                    {release.title}
                  </h3>
                  <p className="text-gray-300 text-sm drop-shadow-sm">
                    {release.podcast}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Featured Podcasts */}
      <section className="mb-6 sm:mb-8">
        <div className="flex items-center justify-between mb-4 sm:mb-6">
          <h2 className="text-xl sm:text-2xl font-bold text-white">Featured Podcasts</h2>
          <button className="text-sm sm:text-base text-gray-400 hover:text-white transition-colors">
            See all
          </button>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-3 sm:gap-4">
          {featuredPodcasts.map((podcast, index) => (
            <div
              key={index}
              className="group cursor-pointer"
            >
              <div className={`${podcast.color} aspect-square rounded-lg mb-3 flex items-center justify-center group-hover:scale-105 transition-transform duration-200`}>
                <div className="w-12 h-12 sm:w-16 sm:h-16 bg-white/20 rounded-full flex items-center justify-center">
                  <div className="w-6 h-6 sm:w-8 sm:h-8 bg-white/30 rounded-full"></div>
                </div>
              </div>
              <h3 className="text-white font-semibold mb-1 group-hover:underline text-sm sm:text-base truncate">
                {podcast.title}
              </h3>
              <p className="text-gray-400 text-xs sm:text-sm truncate">
                {podcast.author}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* Trending Episodes */}
      <section>
        <div className="flex items-center justify-between mb-4 sm:mb-6">
          <h2 className="text-xl sm:text-2xl font-bold text-white">Trending Episodes</h2>
          <button className="text-sm sm:text-base text-gray-400 hover:text-white transition-colors">
            See all
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {trendingEpisodes.map((episode, index) => (
            <div
              key={index}
              className="backdrop-blur-md bg-white/10 border border-white/20 rounded-xl p-4 hover:bg-white/15 hover:border-white/30 transition-all duration-300 cursor-pointer group shadow-lg hover:shadow-xl hover:shadow-white/10"
            >
              <div className="flex items-center space-x-4">
                {/* Profile Image */}
                <div className={`w-16 h-16 ${episode.avatar} rounded-xl flex items-center justify-center flex-shrink-0 overflow-hidden shadow-md`}>
                  <div className="w-10 h-10 bg-white/30 rounded-lg flex items-center justify-center backdrop-blur-sm">
                    <div className="w-6 h-6 bg-white/50 rounded-md"></div>
                  </div>
                </div>
                
                {/* Episode Info */}
                <div className="flex-1 min-w-0">
                  <h3 className="text-white font-semibold mb-1 group-hover:underline text-base line-clamp-2 leading-tight drop-shadow-sm">
                    {episode.title}
                  </h3>
                  <p className="text-gray-300 text-sm drop-shadow-sm">
                    {episode.podcast}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
