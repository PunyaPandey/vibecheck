import { useState } from 'react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
    const [query, setQuery] = useState('')
    const [result, setResult] = useState(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')

    const checkVibe = async () => {
        if (!query) return;

        setLoading(true)
        setError('')
        setResult(null)

        try {
            const response = await fetch(`${API_URL}/analyze?title=${encodeURIComponent(query)}`)
            if (!response.ok) {
                throw new Error('Failed to fetch vibe analysis')
            }
            const data = await response.json()
            setResult(data)
        } catch (err) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="min-h-screen bg-gray-900 text-white font-sans flex flex-col items-center py-10 px-4">
            <h1 className="text-5xl font-extrabold mb-8 text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-600">
                VibeCheck
            </h1>

            <div className="w-full max-w-md flex gap-2 mb-10">
                <input
                    type="text"
                    className="flex-1 p-3 rounded-lg bg-gray-800 border border-gray-700 focus:outline-none focus:border-purple-500 text-white placeholder-gray-500"
                    placeholder="Enter a movie title..."
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && checkVibe()}
                />
                <button
                    onClick={checkVibe}
                    disabled={loading}
                    className="bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-6 rounded-lg transition-colors disabled:opacity-50"
                >
                    {loading ? 'Checking...' : 'Check Vibe'}
                </button>
            </div>

            {error && (
                <div className="text-red-400 mb-8">{error}</div>
            )}

            {result && (
                <div className="bg-gray-800 rounded-xl shadow-2xl p-6 w-full max-w-2xl flex flex-col md:flex-row gap-8 animate-fade-in">
                    {result.poster_url && (
                        <img
                            src={result.poster_url}
                            alt={result.movie_title}
                            className="w-full md:w-1/3 rounded-lg shadow-lg object-cover"
                        />
                    )}

                    <div className="flex-1 flex flex-col">
                        <h2 className="text-3xl font-bold mb-2">{result.movie_title}</h2>
                        <p className="text-gray-300 italic mb-4">"{result.analysis.sentiment_summary}"</p>

                        <div className="mb-6">
                            <h3 className="text-sm uppercase tracking-wider text-gray-500 font-semibold mb-2">Vibe Tags</h3>
                            <div className="flex flex-wrap gap-2">
                                {result.analysis.vibe_tags.map((tag, index) => (
                                    <span key={index} className="px-3 py-1 bg-gray-700 rounded-full text-sm text-purple-300 border border-gray-600">
                                        #{tag}
                                    </span>
                                ))}
                            </div>
                        </div>

                        <div>
                            <div className="flex justify-between items-end mb-1">
                                <h3 className="text-sm uppercase tracking-wider text-gray-500 font-semibold">Intensity Score</h3>
                                <span className="text-2xl font-bold text-pink-500">{result.analysis.intensity_score}/10</span>
                            </div>
                            <div className="w-full bg-gray-700 rounded-full h-2.5">
                                <div
                                    className="bg-gradient-to-r from-purple-500 to-pink-500 h-2.5 rounded-full transition-all duration-1000 ease-out"
                                    style={{ width: `${(result.analysis.intensity_score / 10) * 100}%` }}
                                ></div>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}

export default App
