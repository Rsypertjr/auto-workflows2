// vitest.config.ts
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true, // 👈 Adds expect to the global scope
    setupFiles: ['./vitest.setup.ts'], // 👈 Runs setup before tests
  },
})
