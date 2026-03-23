// tailwind.config.ts
import type { Config } from 'tailwindcss'

const config: Config = {
  content: ['./src/**/*.{js,ts,jsx,tsx,mdx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        bg:          '#0f1117',
        'bg-card':   '#1a1d2e',
        'bg-sidebar':'#14172a',
        'bg-hover':  '#22253a',
        'bg-input':  '#1e2236',
        border:      '#2a2d40',
        primary:     '#3b82f6',
        success:     '#22c55e',
        danger:      '#ef4444',
        warning:     '#f59e0b',
        gold:        '#ffd700',
        teal:        '#2dd4bf',
      },
      fontFamily: {
        hanzi: ['"Noto Sans SC"', '"PingFang SC"', 'serif'],
      },
      animation: {
        'fade-in': 'fadeIn 0.25s ease forwards',
        'slide-up': 'slideUp 0.3s ease forwards',
      },
      keyframes: {
        fadeIn: { from: { opacity: '0', transform: 'translateY(8px)' }, to: { opacity: '1', transform: 'translateY(0)' } },
        slideUp: { from: { opacity: '0', transform: 'translateY(20px)' }, to: { opacity: '1', transform: 'translateY(0)' } },
      },
    },
  },
  plugins: [],
}
export default config
