import React from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { 
  FileText, 
  Briefcase, 
  PenTool, 
  Linkedin, 
  MessageSquare, 
  DollarSign, 
  LayoutDashboard,
  Sparkles,
  Menu,
  X,
  Crown
} from 'lucide-react';
import useAppStore from '../stores/appStore';

const navItems = [
  { path: '/', label: 'Home', icon: Sparkles },
  { path: '/resume-analyzer', label: 'Resume Analyzer', icon: FileText },
  { path: '/job-matcher', label: 'Job Matcher', icon: Briefcase },
  { path: '/cover-letter', label: 'Cover Letter', icon: PenTool },
  { path: '/linkedin-optimizer', label: 'LinkedIn', icon: Linkedin },
  { path: '/interview-prep', label: 'Interview Prep', icon: MessageSquare },
  { path: '/salary-negotiation', label: 'Salary Negotiation', icon: DollarSign },
  { path: '/application-tracker', label: 'Application Tracker', icon: LayoutDashboard },
];

function Layout() {
  const location = useLocation();
  const { sidebarOpen, setSidebarOpen, user } = useAppStore();

  return (
    <div className="flex min-h-screen bg-slate-50">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside 
        className={`
          fixed lg:static inset-y-0 left-0 z-50
          w-64 bg-white border-r border-slate-200
          transform transition-transform duration-300 ease-in-out
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        `}
      >
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="p-6 border-b border-slate-200">
            <Link to="/" className="flex items-center gap-2">
              <div className="w-10 h-10 rounded-xl gradient-primary flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="font-bold text-lg text-slate-900">CareerGenius</h1>
                <p className="text-xs text-slate-500">AI Career Optimization</p>
              </div>
            </Link>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={() => setSidebarOpen(false)}
                  className={`
                    flex items-center gap-3 px-4 py-3 rounded-lg
                    transition-colors duration-200
                    ${isActive 
                      ? 'bg-primary-50 text-primary-700 font-medium' 
                      : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'}
                  `}
                >
                  <Icon className={`w-5 h-5 ${isActive ? 'text-primary-600' : ''}`} />
                  {item.label}
                </Link>
              );
            })}
          </nav>

          {/* User section */}
          <div className="p-4 border-t border-slate-200">
            {user ? (
              <div className="flex items-center gap-3 px-4 py-2">
                <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center">
                  <span className="text-sm font-medium text-primary-700">
                    {user.name?.charAt(0)?.toUpperCase()}
                  </span>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-slate-900 truncate">{user.name}</p>
                  <p className="text-xs text-slate-500 truncate">{user.email}</p>
                </div>
              </div>
            ) : (
              <Link
                to="/pricing"
                className="flex items-center gap-2 px-4 py-2 text-sm text-primary-600 hover:text-primary-700"
              >
                <Crown className="w-4 h-4" />
                Upgrade to Pro
              </Link>
            )}
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Mobile header */}
        <header className="lg:hidden bg-white border-b border-slate-200 px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setSidebarOpen(true)}
              className="p-2 -ml-2 text-slate-600 hover:text-slate-900"
            >
              <Menu className="w-6 h-6" />
            </button>
            <span className="font-semibold text-slate-900">CareerGenius</span>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 p-4 lg:p-8 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

export default Layout;
