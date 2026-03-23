// app/layout.tsx
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Toaster } from 'react-hot-toast'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'HanziFlow — Learn Chinese',
  description: 'AI-powered Chinese learning app',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} bg-[#0f1117] text-white min-h-screen`}>
        {children}
        <Toaster
          position="bottom-right"
          toastOptions={{
            style: { background: '#1e2236', color: '#f1f5f9', border: '1px solid #2a2d40' },
          }}
        />
      </body>
    </html>
  )
}
