/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        chess: {
          boardLight: '#f0d9b5',
          boardDark: '#b58863',
          highlight: '#7b61ff',
          selected: '#bbc92e',
        }
      }
    },
  },
  plugins: [],
}
