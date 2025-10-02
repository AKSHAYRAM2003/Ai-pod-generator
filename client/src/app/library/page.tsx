export default function Library() {
  const savedPodcasts = [
    {
      title: "AI Revolution Series",
      author: "Tech Innovators",
      episodes: 24,
      color: "bg-gradient-to-br from-purple-400 to-pink-500"
    },
    {
      title: "Future of Work",
      author: "Business Leaders",
      episodes: 18,
      color: "bg-gradient-to-br from-blue-400 to-cyan-500"
    },
    {
      title: "Digital Transformation",
      author: "Tech Experts",
      episodes: 32,
      color: "bg-gradient-to-br from-green-400 to-teal-500"
    },
    {
      title: "Startup Stories",
      author: "Entrepreneur Hub",
      episodes: 15,
      color: "bg-gradient-to-br from-orange-400 to-red-500"
    }
  ];

  const recentlyPlayed = [
    {
      title: "The Rise of Generative AI",
      podcast: "AI Revolution Series",
      duration: "45:32",
      avatar: "bg-gradient-to-br from-purple-400 to-pink-500"
    },
    {
      title: "Remote Work Technologies",
      podcast: "Future of Work",
      duration: "38:15",
      avatar: "bg-gradient-to-br from-blue-400 to-cyan-500"
    },
    {
      title: "Cloud Computing Trends",
      podcast: "Digital Transformation",
      duration: "42:08",
      avatar: "bg-gradient-to-br from-green-400 to-teal-500"
    }
  ];

  return (
    <main className="flex-1 bg-black p-4 sm:p-6 lg:p-8 overflow-y-auto">
      <div className="mb-6 sm:mb-8">
        <h1 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold text-white mb-2">
          Your Library
        </h1>
        <p className="text-gray-400 text-sm sm:text-base md:text-lg">
          Your saved podcasts and listening history.
        </p>
      </div>

      {/* Recently Played */}
      <section className="mb-6 sm:mb-8">
        <div className="flex items-center justify-between mb-4 sm:mb-6">
          <h2 className="text-xl sm:text-2xl font-bold text-white">Recently Played</h2>
          <button className="text-sm sm:text-base text-gray-400 hover:text-white transition-colors">
            See all
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {recentlyPlayed.map((episode, index) => (
            <div
              key={index}
              className="backdrop-blur-md bg-white/10 border border-white/20 rounded-xl p-4 hover:bg-white/15 hover:border-white/30 transition-all duration-300 cursor-pointer group shadow-lg hover:shadow-xl hover:shadow-white/10"
            >
              <div className="flex items-center space-x-4">
                <div className={`w-16 h-16 ${episode.avatar} rounded-xl flex items-center justify-center flex-shrink-0 overflow-hidden shadow-md`}>
                  <div className="w-10 h-10 bg-white/30 rounded-lg flex items-center justify-center backdrop-blur-sm">
                    <div className="w-6 h-6 bg-white/50 rounded-md"></div>
                  </div>
                </div>
                
                <div className="flex-1 min-w-0">
                  <h3 className="text-white font-semibold mb-1 group-hover:underline text-base line-clamp-2 leading-tight drop-shadow-sm">
                    {episode.title}
                  </h3>
                  <p className="text-gray-300 text-sm drop-shadow-sm mb-1">
                    {episode.podcast}
                  </p>
                  <p className="text-gray-400 text-xs">
                    {episode.duration}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Saved Podcasts */}
      <section>
        <div className="flex items-center justify-between mb-4 sm:mb-6">
          <h2 className="text-xl sm:text-2xl font-bold text-white">Saved Podcasts</h2>
          <button className="text-sm sm:text-base text-gray-400 hover:text-white transition-colors">
            See all
          </button>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-3 sm:gap-4">
          {savedPodcasts.map((podcast, index) => (
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
                {podcast.author} • {podcast.episodes} episodes
              </p>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
