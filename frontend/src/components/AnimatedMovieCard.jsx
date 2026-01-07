import React, { useEffect, useState } from 'react';
import { motion, useAnimation } from 'framer-motion';

const AnimatedMovieCard = ({ result }) => {
    if (!result) return null;

    const { movie_title, poster_url, generated_image_url, analysis } = result;

    // Staggered list variants
    const containerVariants = {
        hidden: { opacity: 0 },
        show: {
            opacity: 1,
            transition: {
                staggerChildren: 0.1
            }
        }
    };

    const itemVariants = {
        hidden: { opacity: 0, y: 10 },
        show: { opacity: 1, y: 0 }
    };

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 30 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            transition={{ duration: 0.6, type: "spring" }}
            className="w-full max-w-5xl mx-auto mt-8 perspective-1000"
        >
            <motion.div
                className="bg-gray-900/60 backdrop-blur-xl border border-gray-700/50 rounded-3xl p-6 md:p-8 shadow-2xl flex flex-col md:flex-row gap-8 overflow-hidden relative"
                whileHover={{
                    rotateX: 1,
                    rotateY: 1,
                    boxShadow: "0 25px 50px -12px rgba(124, 58, 237, 0.25)"
                }}
                transition={{ type: "spring", stiffness: 300, damping: 20 }}
                style={{ transformStyle: "preserve-3d" }}
            >
                {/* Decorative background blob inside card */}
                <div className="absolute -top-20 -right-20 w-64 h-64 bg-purple-600/20 rounded-full blur-3xl pointer-events-none" />

                {/* Visuals Column */}
                <div className="flex flex-col gap-4 w-full md:w-1/3 shrink-0 z-10">
                    {poster_url && (
                        <motion.div
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: 0.2 }}
                            className="relative group rounded-xl overflow-hidden shadow-black/50 shadow-lg"
                        >
                            <img
                                src={poster_url}
                                alt={movie_title}
                                className="w-full h-auto object-cover transition-transform duration-700 group-hover:scale-105"
                            />
                            <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-end p-4">
                                <span className="text-white text-xs font-bold uppercase tracking-wider">Original Poster</span>
                            </div>
                        </motion.div>
                    )}

                    {generated_image_url && (
                        <motion.div
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: 0.4 }}
                            className="relative group rounded-xl overflow-hidden shadow-black/50 shadow-lg border-2 border-purple-500/50"
                        >
                            <img
                                src={generated_image_url}
                                alt="AI Generated Vibe"
                                className="w-full h-auto object-cover transition-transform duration-700 group-hover:scale-110"
                            />
                            <div className="absolute bottom-3 right-3 bg-purple-600/90 text-white text-xs font-bold px-3 py-1 rounded-full shadow-lg backdrop-blur-sm">
                                AI Vibe Art
                            </div>
                        </motion.div>
                    )}
                </div>

                {/* Content Column */}
                <div className="flex-1 flex flex-col z-10">
                    <motion.h2
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.3 }}
                        className="text-4xl md:text-5xl font-black mb-4 text-transparent bg-clip-text bg-gradient-to-r from-white to-gray-400"
                    >
                        {movie_title}
                    </motion.h2>

                    <motion.p
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.4 }}
                        className="text-lg text-gray-300 italic mb-6 leading-relaxed border-l-4 border-purple-500 pl-4 py-1"
                    >
                        "{analysis.sentiment_summary}"
                    </motion.p>

                    <div className="mb-8">
                        <h3 className="text-xs uppercase tracking-[0.2em] text-gray-500 font-bold mb-4 flex items-center gap-2">
                            <span className="w-8 h-[1px] bg-gray-600"></span>
                            Vibe Tags
                        </h3>
                        <motion.div
                            variants={containerVariants}
                            initial="hidden"
                            animate="show"
                            className="flex flex-wrap gap-2"
                        >
                            {(analysis.vibe_tags || []).map((tag, index) => (
                                <motion.span
                                    key={index}
                                    variants={itemVariants}
                                    whileHover={{ scale: 1.1, backgroundColor: "rgba(139, 92, 246, 0.4)" }}
                                    className="px-4 py-2 bg-gray-800/50 border border-gray-600 rounded-lg text-sm font-medium text-purple-200 shadow-sm cursor-default"
                                >
                                    #{tag}
                                </motion.span>
                            ))}
                        </motion.div>
                    </div>

                    <div className="mt-auto bg-gray-800/30 p-6 rounded-2xl border border-gray-700/30">
                        <div className="flex justify-between items-end mb-2">
                            <h3 className="text-xs uppercase tracking-[0.2em] text-gray-500 font-bold">Intensity Score</h3>
                            <motion.span
                                initial={{ opacity: 0, scale: 0.5 }}
                                animate={{ opacity: 1, scale: 1 }}
                                transition={{ delay: 1, type: "spring" }}
                                className="text-3xl font-black text-pink-500"
                            >
                                {analysis.intensity_score}<span className="text-lg text-gray-600">/10</span>
                            </motion.span>
                        </div>
                        <div className="w-full bg-gray-700/50 rounded-full h-3 overflow-hidden">
                            <motion.div
                                initial={{ width: 0 }}
                                animate={{ width: `${(analysis.intensity_score / 10) * 100}%` }}
                                transition={{ duration: 1.5, ease: "easeOut", delay: 0.5 }}
                                className="bg-gradient-to-r from-purple-600 via-pink-500 to-red-500 h-full rounded-full relative"
                            >
                                <div className="absolute inset-0 bg-white/20 animate-pulse"></div>
                            </motion.div>
                        </div>
                    </div>
                </div>
            </motion.div>
        </motion.div>
    );
};

export default AnimatedMovieCard;
