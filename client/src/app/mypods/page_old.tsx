import ProtectedRouteWrapper from '@/components/ProtectedRouteWrapper';

export default function MyPods() {
  const myGeneratedPodcasts = [
    {
      title: "My AI Journey",
      author: "You",
      episodes: 5,
      createdAt: "2 days ago",
      color: "bg-gradient-to-br from-purple-500 to-pink-600"
    },
    {
      title: "Tech Insights Weekly",
      author: "You",
      episodes: 12,
      createdAt: "1 week ago",
      color: "bg-gradient-to-br from-blue-500 to-cyan-600"
    },
    {
      title: "Business Strategy Talk",
      author: "You",
      episodes: 8,
      createdAt: "2 weeks ago",
      color: "bg-gradient-to-br from-green-500 to-teal-600"
    },
    {
      title: "Creative Coding",
      author: "You",
      episodes: 15,
      createdAt: "3 weeks ago",
      color: "bg-gradient-to-br from-orange-500 to-red-600"
    }
  ];

  const recentEpisodes = [
    {
      title: "Getting Started with AI Podcast Generation",
      podcast: "My AI Journey",
      duration: "42:15",
      createdAt: "Yesterday",
      avatar: "bg-gradient-to-br from-purple-500 to-pink-600"
    },
    {
      title: "Understanding Machine Learning Basics",
      podcast: "Tech Insights Weekly",
      duration: "35:48",
      createdAt: "2 days ago",
      avatar: "bg-gradient-to-br from-blue-500 to-cyan-600"
    },
    {
      title: "Building a Successful Startup",
      podcast: "Business Strategy Talk",
      duration: "48:22",
      createdAt: "5 days ago",
      avatar: "bg-gradient-to-br from-green-500 to-teal-600"
    }
  ];

  return (
    <ProtectedRouteWrapper>
    <main className="flex-1 bg-black p-4 sm:p-6 lg:p-8 overflow-y-auto">
      <div className="mb-6 sm:mb-8">
        <h1 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold text-white mb-2">
          My Pods
        </h1>
        <p className="text-gray-400 text-sm sm:text-base md:text-lg">
          Your AI-generated podcasts and episodes.
        </p>
      </div>

      {/* Recently Created Episodes */}
      <section className="mb-6 sm:mb-8">
        <div className="flex items-center justify-between mb-4 sm:mb-6">
          <h2 className="text-xl sm:text-2xl font-bold text-white">Recently Created</h2>
          <button className="text-sm sm:text-base text-gray-400 hover:text-white transition-colors">
            See all
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {recentEpisodes.map((episode, index) => (
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
                  <div className="flex items-center gap-2 text-gray-400 text-xs">
                    <span>{episode.duration}</span>
                    <span>•</span>
                    <span>{episode.createdAt}</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* My Generated Podcasts */}
      <section>
        <div className="flex items-center justify-between mb-4 sm:mb-6">
          <h2 className="text-xl sm:text-2xl font-bold text-white">My Podcasts</h2>
          <button className="px-4 py-2 bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 text-white font-medium rounded-full text-sm transition-all duration-200 shadow-lg hover:shadow-blue-500/50">
            + Create New
          </button>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-3 sm:gap-4">
          {myGeneratedPodcasts.map((podcast, index) => (
            <div
              key={index}
              className="group cursor-pointer"
            >
              <div className={`${podcast.color} aspect-square rounded-lg mb-3 flex items-center justify-center group-hover:scale-105 transition-transform duration-200 shadow-lg`}>
                <div className="w-12 h-12 sm:w-16 sm:h-16 bg-white/20 rounded-full flex items-center justify-center">
                  <div className="w-6 h-6 sm:w-8 sm:h-8 bg-white/30 rounded-full"></div>
                </div>
              </div>
              <h3 className="text-white font-semibold mb-1 group-hover:underline text-sm sm:text-base truncate">
                {podcast.title}
              </h3>
              <p className="text-gray-400 text-xs sm:text-sm truncate">
                {podcast.episodes} episodes • {podcast.createdAt}
              </p>
            </div>
          ))}
        </div>

        {/* Empty State - Show if no podcasts */}
        {myGeneratedPodcasts.length === 0 && (
          <div className="text-center py-12">
            <div className="w-24 h-24 bg-gradient-to-br from-purple-500 to-pink-600 rounded-full mx-auto mb-4 flex items-center justify-center opacity-50">
              <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">No podcasts yet</h3>
            <p className="text-gray-400 mb-4">Start creating your first AI-powered podcast</p>
            <button className="px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-medium rounded-full transition-all duration-200 shadow-lg hover:shadow-purple-500/50">
              Create Your First Podcast
            </button>
          </div>
        )}
      </section>
    </main>
    </ProtectedRouteWrapper>
  );
}
