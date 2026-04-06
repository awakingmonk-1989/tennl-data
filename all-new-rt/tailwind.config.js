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
          DEFAULT: '#FF6B35',
          light: '#FF8C5A',
          pale: '#FFF0EA',
        },
        accent: {
          DEFAULT: '#FFB347',
          light: '#FFD080',
          pale: '#FFF8EC',
        },
        xlife: '#FF6B35',
        xdiscover: '#2DD4BF',
        xai: '#A78BFA',
        bg: {
          DEFAULT: '#FAFAF8',
          card: '#FFFFFF',
          warm: '#FFF5F0',
          amber: '#FFFBF0',
        },
        fg: {
          DEFAULT: '#1A1A1A',
          muted: '#6B6B6B',
          subtle: '#A8A8A8',
        },
        border: {
          DEFAULT: '#EBEBEB',
          warm: '#FFD5C2',
        },
      },
      fontFamily: {
        display: ['Plus Jakarta Sans', 'sans-serif'],
        body: ['DM Sans', 'sans-serif'],
        sans: ['DM Sans', 'sans-serif'],
      },
      fontSize: {
        'display-xl': ['clamp(3.5rem, 10vw, 9rem)', { lineHeight: '0.88', letterSpacing: '-0.04em' }],
        'display-lg': ['clamp(2.5rem, 6vw, 6rem)', { lineHeight: '0.9', letterSpacing: '-0.03em' }],
        'display-md': ['clamp(1.75rem, 4vw, 3.5rem)', { lineHeight: '1.1', letterSpacing: '-0.025em' }],
      },
      borderRadius: {
        '2xl': '20px',
        '3xl': '24px',
        '4xl': '32px',
      },
      boxShadow: {
        'warm-sm': '0 4px 20px -4px rgba(255, 107, 53, 0.1)',
        'warm-md': '0 12px 40px -8px rgba(255, 107, 53, 0.15)',
        'warm-lg': '0 20px 60px -10px rgba(255, 107, 53, 0.2)',
        'card': '0 2px 20px rgba(0, 0, 0, 0.06)',
        'card-hover': '0 20px 50px -10px rgba(255, 107, 53, 0.12)',
      },
      animation: {
        'blob-float': 'blobFloat 8s ease-in-out infinite',
        'blob-float-2': 'blobFloat2 10s ease-in-out infinite',
        'float': 'float 4s ease-in-out infinite',
        'float-slow': 'float 6s ease-in-out infinite',
        'spin-slow': 'spinSlow 20s linear infinite',
        'pulse-ring': 'pulseRing 2s ease-out infinite',
      },
      keyframes: {
        blobFloat: {
          '0%, 100%': { transform: 'translate(0, 0) scale(1)' },
          '33%': { transform: 'translate(20px, -20px) scale(1.05)' },
          '66%': { transform: 'translate(-15px, 10px) scale(0.97)' },
        },
        blobFloat2: {
          '0%, 100%': { transform: 'translate(0, 0) scale(1)' },
          '33%': { transform: 'translate(-25px, 15px) scale(1.08)' },
          '66%': { transform: 'translate(20px, -10px) scale(0.95)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-12px)' },
        },
        spinSlow: {
          from: { transform: 'rotate(0deg)' },
          to: { transform: 'rotate(360deg)' },
        },
        pulseRing: {
          '0%': { transform: 'scale(1)', opacity: '0.8' },
          '100%': { transform: 'scale(1.8)', opacity: '0' },
        },
      },
      backgroundImage: {
        'warm-gradient': 'linear-gradient(135deg, #FAFAF8 0%, #FFF5F0 50%, #FFFBF0 100%)',
        'coral-gradient': 'linear-gradient(135deg, #FF6B35 0%, #FFB347 100%)',
        'teal-gradient': 'linear-gradient(135deg, #2DD4BF 0%, #06B6D4 100%)',
        'purple-gradient': 'linear-gradient(135deg, #A78BFA 0%, #EC4899 100%)',
      },
    },
  },
  plugins: [],
};
