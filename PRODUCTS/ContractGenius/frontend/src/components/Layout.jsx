import React from 'react'
import { Link } from 'react-router-dom'
import { Scale, Github, Twitter, Linkedin } from 'lucide-react'

const Layout = ({ children }) => {
  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-gray-50 to-blue-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link to="/" className="flex items-center space-x-2 group">
              <div className="bg-primary-600 p-2 rounded-lg group-hover:bg-primary-700 transition-colors">
                <Scale className="h-6 w-6 text-white" />
              </div>
              <span className="text-xl font-bold text-gray-900">
                Contract
                <span className="text-primary-600">Genius</span>
              </span>
            </Link>
            
            <nav className="flex items-center space-x-6">
              <a 
                href="https://github.com" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-gray-500 hover:text-gray-700 transition-colors"
              >
                <Github className="h-5 w-5" />
              </a>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-grow">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center space-x-2 mb-4 md:mb-0">
              <Scale className="h-5 w-5 text-primary-600" />
              <span className="font-semibold text-gray-900">ContractGenius</span>
            </div>
            
            <p className="text-gray-500 text-sm">
              © 2024 ContractGenius. AI-Powered Legal Contract Analysis.
            </p>
            
            <div className="flex items-center space-x-4 mt-4 md:mt-0">
              <a href="#" className="text-gray-400 hover:text-gray-600">
                <Twitter className="h-5 w-5" />
              </a>
              <a href="#" className="text-gray-400 hover:text-gray-600">
                <Linkedin className="h-5 w-5" />
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default Layout