import React from 'react';
import { motion } from 'framer-motion';
// Wait, user didn't ask for lucide-react. I should stick to basic text or SVGs if I don't want to add more deps. 
// Or I can use simple SVG icons inline to be safe and dependent-free.

const steps = [
    {
        title: "Pick a Movie",
        description: "Enter any movie title to start the vibe check.",
        icon: (
            <svg className="w-8 h-8 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
        )
    },
    {
        title: "AI Analysis",
        description: "Our Llama-3 AI reads reviews to detect the hidden vibe.",
        icon: (
            <svg className="w-8 h-8 text-pink-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.384-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
            </svg>
        )
    },
    {
        title: "See the Score",
        description: "Get a Vibe Score and a custom AI-generated poster.",
        icon: (
            <svg className="w-8 h-8 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
        )
    }
];

const OnboardingTour = () => {
    return (
        <div className="w-full max-w-4xl mx-auto mt-12 grid grid-cols-1 md:grid-cols-3 gap-6 px-4">
            {steps.map((step, index) => (
                <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.2, duration: 0.5 }}
                    whileHover={{ scale: 1.05, borderColor: 'rgba(167, 139, 250, 0.5)' }}
                    className="bg-gray-900/50 backdrop-blur-md border border-gray-800 p-6 rounded-2xl flex flex-col items-center text-center hover:bg-gray-800/50 transition-colors cursor-default"
                >
                    <div className="mb-4 p-3 bg-gray-800/80 rounded-full shadow-lg shadow-purple-900/20">
                        {step.icon}
                    </div>
                    <h3 className="text-xl font-bold text-gray-100 mb-2">{step.title}</h3>
                    <p className="text-gray-400 text-sm">{step.description}</p>
                </motion.div>
            ))}
        </div>
    );
};

export default OnboardingTour;
