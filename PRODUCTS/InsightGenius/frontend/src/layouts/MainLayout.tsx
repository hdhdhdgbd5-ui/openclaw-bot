import { Outlet } from 'react-router-dom'
import Sidebar from '../components/Sidebar'
import Header from '../components/Header'
import { useEffect } from 'react'
import { wsService } from '../services/api'

export default function MainLayout() {
  useEffect(() => {
    // Connect to WebSocket for real-time updates
    wsService.connect()
    
    return () => {
      wsService.disconnect()
    }
  }, [])

  return (
    <div className="min-h-screen bg-dark-900 text-white">
      <Sidebar />
      <div className="ml-64">
        <Header />
        <main className="p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
