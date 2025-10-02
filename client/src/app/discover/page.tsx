export default function Discover() {
  return (
    <main className="flex-1 bg-black p-4 sm:p-6 lg:p-8 overflow-y-auto">
      <div className="mb-6 sm:mb-8">
        <h1 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold text-white mb-2">
          Discover Podcasts
        </h1>
        <p className="text-gray-400 text-sm sm:text-base md:text-lg">
          Explore new and trending AI-powered audio content.
        </p>
      </div>

      {/* Browse Categories */}
      <section className="mb-6 sm:mb-8">
        <h2 className="text-xl sm:text-2xl font-bold text-white mb-4 sm:mb-6">Browse Categories</h2>
        
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
          {[
            { name: "Technology", color: "bg-gradient-to-br from-blue-500 to-purple-600" },
            { name: "Science", color: "bg-gradient-to-br from-green-500 to-teal-600" },
            { name: "Business", color: "bg-gradient-to-br from-orange-500 to-red-600" },
            { name: "Education", color: "bg-gradient-to-br from-indigo-500 to-blue-600" },
            { name: "Health", color: "bg-gradient-to-br from-pink-500 to-rose-600" },
            { name: "Entertainment", color: "bg-gradient-to-br from-yellow-500 to-orange-600" },
            { name: "News", color: "bg-gradient-to-br from-purple-500 to-indigo-600" },
            { name: "Sports", color: "bg-gradient-to-br from-cyan-500 to-blue-600" },
          ].map((category, index) => (
            <div
              key={index}
              className={`${category.color} rounded-lg p-6 cursor-pointer hover:scale-105 transition-transform duration-200`}
            >
              <h3 className="text-white font-semibold text-lg">{category.name}</h3>
            </div>
          ))}
        </div>
      </section>

      {/* Popular Searches */}
      <section>
        <h2 className="text-xl sm:text-2xl font-bold text-white mb-4 sm:mb-6">Popular Searches</h2>
        
        <div className="flex flex-wrap gap-2">
          {[
            "AI Technology", "Machine Learning", "Data Science", "Blockchain",
            "Virtual Reality", "Cybersecurity", "Startups", "Programming",
            "Innovation", "Future Tech", "Automation", "Digital Transformation"
          ].map((tag, index) => (
            <span
              key={index}
              className="bg-gray-800 hover:bg-gray-700 text-white px-4 py-2 rounded-full cursor-pointer transition-colors duration-200"
            >
              {tag}
            </span>
          ))}
        </div>
      </section>
    </main>
  );
}
