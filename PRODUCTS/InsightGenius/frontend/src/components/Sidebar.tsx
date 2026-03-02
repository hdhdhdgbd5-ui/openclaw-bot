import { NavLink } from 'react-router-dom'
import { useState } from 'react'
import {
  HomeIcon,
  ChartBarIcon,
  CircleStackIcon,
  CloudArrowUpIcon,
  PresentationChartLineIcon,
  BellIcon,
  DocumentTextIcon,
  Cog6ToothIcon,
  SparklesIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
} from '@heroicons/react/24/outline'

const navigation = [
  { name: 'Dashboards', href: '/dashboards', icon: HomeIcon },
  { name: 'Datasets', href: '/datasets', icon: CircleStackIcon },
  { name: 'Data Sources', href: '/data-sources', icon: CloudArrowUpIcon },
  { name: 'Visualizations', href: '/visualizations', icon: ChartBarIcon },
  { name: 'ML Models', href: '/ml-models', icon: SparklesIcon },
  { name: 'Predictions', href: '/predictions', icon: PresentationChartLineIcon },
  { name: 'Alerts', href: '/alerts', icon: BellIcon },
  { name: 'Reports', href: '/reports', icon: DocumentTextIcon },
  { name: 'Settings', href: '/settings', icon: Cog6ToothIcon },
]

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false)

  return (
    <div 
      className={`fixed left-0 top-0 h-full bg-dark-800 border-r border-dark-700 transition-all duration-300 z-50 ${
        collapsed ? 'w-20' : 'w-64'
      }`}
    >
      <div className="h-full flex flex-col">
        {/* Logo */}
        <div className="h-16 flex items-center px-4 border-b border-dark-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-accent-purple flex items-center justify-center flex-shrink-0">
              <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            {!collapsed && (
              <span className="font-bold text-lg text-white">InsightGenius</span>
            )}
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-3 py-4 space-y-1">
          {navigation.map((item) => (
            <NavLink
              key={item.name}
              to={item.href}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-primary-500/10 text-primary-400 border border-primary-500/20'
                    : 'text-gray-400 hover:bg-dark-700 hover:text-white'
                }`
              }
            >
              <item.icon className="w-5 h-5 flex-shrink-0" />
              {!collapsed && <span>{item.name}</span>}
            </NavLink>
          ))}
        </nav>

        {/* Collapse button */}
        <div className="p-3 border-t border-dark-700">
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="w-full flex items-center justify-center p-2 rounded-lg text-gray-400 hover:bg-dark-700 hover:text-white transition-colors"
          >
            {collapsed ? (
              <ChevronRightIcon className="w-5 h-5" />
            ) : (
              <ChevronLeftIcon className="w-5 h-5" />
            )}
          </button>
        </div>
      </div>
    </div>
  )
}
