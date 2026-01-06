import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react()],
    server: {
        proxy: {
            // Optional proxy for local dev if needed, 
            // though we are using CORS on backend to allow cross-origin
        }
    }
})
