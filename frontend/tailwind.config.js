/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f5f3ff',
          100: '#ede9fe',
          200: '#ddd6fe',
          300: '#c4b5fd',
          400: '#a78bfa',
          500: '#8b5cf6',
          600: '#7c3aed',
          700: '#6d28d9',
          800: '#5b21b6',
          900: '#4c1d95',
          950: '#2e1065',
        },
        medieval: {
          parchment: '#f4e4bc',
          leather: '#8b4513',
          wood: '#654321',
          stone: '#808080',
          gold: '#ffd700',
          silver: '#c0c0c0',
          bronze: '#cd7f32',
        },
      },
      fontFamily: {
        medieval: ['MedievalSharp', 'cursive'],
        fantasy: ['Luminari', 'fantasy'],
      },
      backgroundImage: {
        'parchment-texture': "url('/textures/parchment.png')",
        'stone-texture': "url('/textures/stone.png')",
        'wood-texture': "url('/textures/wood.png')",
      },
    },
  },
  plugins: [],
} 