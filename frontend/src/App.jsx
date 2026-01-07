import { useState } from 'react'
import SpotlightBackground from './components/SpotlightBackground'
import OnboardingTour from './components/OnboardingTour'
import AnimatedMovieCard from './components/AnimatedMovieCard'

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
        <SpotlightBackground>
            <div className="min-h-screen text-white font-sans flex flex-col items-center py-10 px-4 relative z-20">

                {/* Header */}
                <h1 className="text-6xl md:text-8xl font-black mb-12 text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-500 drop-shadow-[0_0_15px_rgba(168,85,247,0.5)] tracking-tighter">
                    VibeCheck
                </h1>

                {/* Search Bar */}
                <div className="w-full max-w-2xl relative group z-30">
                    <div className="absolute -inset-1 bg-gradient-to-r from-purple-600 to-pink-600 rounded-2xl blur opacity-25 group-hover:opacity-75 transition duration-1000 group-hover:duration-200"></div>
                    <div className="relative flex bg-gray-900 ring-1 ring-gray-800/50 rounded-2xl shadow-xl leading-none">
                        <div className="flex items-center pl-6">
                            {loading ? (
                                <div className="w-6 h-6 border-2 border-purple-500 border-t-transparent rounded-full animate-spin"></div>
                            ) : (
                                <svg className="w-6 h-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                                </svg>
                            )}
                        </div>
                        <input
                            type="text"
                            className="w-full p-6 bg-transparent text-gray-100 placeholder-gray-500 focus:outline-none text-xl font-medium"
                            placeholder="Enter a movie title..."
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && checkVibe()}
                        />
                        <button
                            onClick={checkVibe}
                            disabled={loading}
                            className="bg-purple-600 hover:bg-purple-500 text-white font-bold py-4 px-8 rounded-r-2xl transition-all disabled:opacity-50 disabled:cursor-not-allowed m-1 rounded-xl"
                        >
                            Analyze
                        </button>
                    </div>
                </div>

                {/* Main Content Area */}
                <div className="w-full mt-12">
                    {error && (
                        <div className="max-w-md mx-auto bg-red-900/50 border border-red-500/50 text-red-200 p-4 rounded-xl text-center backdrop-blur-sm animate-pulse">
                            {error}
                        </div>
                    )}

                    {/* Show Tour if no result, otherwise show card */}
                    {!result && !loading && !error && (
                        <OnboardingTour />
                    )}

                    {result && (
                        <AnimatedMovieCard result={result} />
                    )}
                </div>

                {/* Footer credit */}
                <div className="fixed bottom-4 text-gray-500 text-xs tracking-widest uppercase opacity-50 pointer-events-none">
                    Powered by Phi-3 Mini & Flux
                </div>
            </div>
        </SpotlightBackground>
    )
}

export default App
