import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { EyeIcon, EyeSlashIcon } from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'

export default function Register() {
  const navigate = useNavigate()
  const { register } = useAuthStore()
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    password: '',
    company: '',
  })
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    
    try {
      await register(formData)
      toast.success('Account created successfully!')
      navigate('/dashboards')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Registration failed')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="w-full">
      <h2 className="text-2xl font-bold text-white mb-2">Create account</h2>
      <p className="text-gray-400 mb-6">Start your 14-day free trial today</p>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1">
            Full Name
          </label>
          <input
            type="text"
            value={formData.full_name}
            onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
            className="w-full px-4 py-3 bg-dark-900 border border-dark-700 rounded-lg text-white focus:ring-2 focus:ring-primary-500"
            placeholder="John Doe"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1">
            Email
          </label>
          <input
            type="email"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            className="w-full px-4 py-3 bg-dark-900 border border-dark-700 rounded-lg text-white focus:ring-2 focus:ring-primary-500"
            placeholder="you@company.com"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1">
            Company (optional)
          </label>
          <input
            type="text"
            value={formData.company}
            onChange={(e) => setFormData({ ...formData, company: e.target.value })}
            className="w-full px-4 py-3 bg-dark-900 border border-dark-700 rounded-lg text-white focus:ring-2 focus:ring-primary-500"
            placeholder="Acme Inc."
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1">
            Password
          </label>
          <div className="relative">
            <input
              type={showPassword ? 'text' : 'password'}
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              className="w-full px-4 py-3 bg-dark-900 border border-dark-700 rounded-lg text-white focus:ring-2 focus:ring-primary-500"
              placeholder="••••••••"
              minLength={8}
              required
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white"
            >
              {showPassword ? <EyeSlashIcon className="w-5 h-5" /> : <EyeIcon className="w-5 h-5" />}
            </button>
          </div>
          <p className="text-xs text-gray-500 mt-1">Must be at least 8 characters</p>
        </div>

        <div className="flex items-start">
          <input 
            type="checkbox" 
            className="mt-1 rounded bg-dark-900 border-dark-700 text-primary-500" 
            required
          />
          <span className="ml-2 text-sm text-gray-400">
            I agree to the{' '}
            <Link to="/terms" className="text-primary-400 hover:text-primary-300">Terms</Link>
            {' '}and{' '}
            <Link to="/privacy" className="text-primary-400 hover:text-primary-300">Privacy Policy</Link>
          </span>
        </div>

        <button
          type="submit"
          disabled={isLoading}
          className="w-full py-3 bg-primary-600 hover:bg-primary-500 disabled:bg-primary-600/50 text-white font-semibold rounded-lg transition-colors"
        >
          {isLoading ? 'Creating account...' : 'Create account'}
        </button>
      </form>

      <p className="mt-6 text-center text-gray-400">
        Already have an account?{' '}
        <Link to="/login" className="text-primary-400 hover:text-primary-300 font-medium">
          Sign in
        </Link>
      </p>
    </div>
  )
}
