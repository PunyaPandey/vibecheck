/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                'vibe-dark': '#0f172a',
                'vibe-card': '#1e293b',
                'vibe-accent': '#38bdf8',
            }
        },
    },
    plugins: [],
}
