import { useState } from 'react'
import { useAuthStore } from '../stores/authStore'
import { BellIcon, MagnifyingGlassIcon, UserCircleIcon } from '@heroicons/react/24/outline'

export default function Header() {
  const { user, logout } = useAuthStore()
  const [showUserMenu, setShowUserMenu] = useState(false)
  const [showNotifications, setShowNotifications] = useState(false)

  return (
    <header className="h-16 bg-dark-800/50 backdrop-blur-sm border-b border-dark-700 flex items-center justify-between px-6 sticky top-0 z-40">
      {/* Search */}
      <div className="flex-1 max-w-xl">
        <div className="relative">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search dashboards, datasets, or ask AI..."
            className="w-full pl-10 pr-4 py-2 bg-dark-900 border border-dark-700 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-4">
        {/* Notifications */}
        <div className="relative">
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            className="relative p-2 text-gray-400 hover:text-white transition-colors"
          >
            <BellIcon className="w-6 h-6" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
          </button>

          {showNotifications && (
            <div className="absolute right-0 mt-2 w-80 bg-dark-800 border border-dark-700 rounded-lg shadow-xl z-50">
              <div className="p-4 border-b border-dark-700">
                <h3 className="font-semibold">Notifications</h3>
              </div>
              <div className="p-4 space-y-3">
                <div className="flex gap-3 text-sm">
                  <div className="w-2 h-2 mt-1.5 bg-red-500 rounded-full flex-shrink-0"></div>
                  <div>
                    <p className="text-white">Sales threshold exceeded</p>
                    <p className="text-gray-500 text-xs">2 minutes ago</p>
                  </div>
                </div>
                <div className="flex gap-3 text-sm">
                  <div className="w-2 h-2 mt-1.5 bg-yellow-500 rounded-full flex-shrink-0"></div>
                  <div>
                    <p className="text-white">ML model training completed</p>
                    <p className="text-gray-500 text-xs">1 hour ago</p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* User menu */}
        <div className="relative">
          <button
            onClick={() => setShowUserMenu(!showUserMenu)}
            className="flex items-center gap-2 text-sm text-gray-300 hover:text-white"
          >
            <UserCircleIcon className="w-8 h-8" />
            <span>{user?.full_name}</span>
          </button>

          {showUserMenu && (
            <div className="absolute right-0 mt-2 w-48 bg-dark-800 border border-dark-700 rounded-lg shadow-xl z-50">
              <div className="p-2">
                <div className="px-3 py-2 text-sm text-gray-400 border-b border-dark-700 mb-2">
                  {user?.email}
                </div>
                <button
                  onClick={() => { logout(); setShowUserMenu(false); }}
                  className="w-full text-left px-3 py-2 text-sm text-red-400 hover:bg-dark-700 rounded-lg"
                >
                  Sign out
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}
