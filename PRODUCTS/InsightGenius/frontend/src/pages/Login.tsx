import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { EyeIcon, EyeSlashIcon } from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'

export default function Login() {
  const navigate = useNavigate()
  const { login } = useAuthStore()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    
    try {
      await login(email, password)
      toast.success('Welcome back!')
      navigate('/dashboards')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Login failed')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="w-full">
      <h2 className="text-2xl font-bold text-white mb-2">Welcome back</h2>
      <p className="text-gray-400 mb-6">Sign in to your InsightGenius account</p>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1">
            Email
          </label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-4 py-3 bg-dark-900 border border-dark-700 rounded-lg text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            placeholder="you@company.com"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1">
            Password
          </label>
          <div className="relative">
            <input
              type={showPassword ? 'text' : 'password'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 bg-dark-900 border border-dark-700 rounded-lg text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="••••••••"
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
        </div>

        <div className="flex items-center justify-between">
          <label className="flex items-center">
            <input type="checkbox" className="rounded bg-dark-900 border-dark-700 text-primary-500" />
            <span className="ml-2 text-sm text-gray-400">Remember me</span>
          </label>
          <Link to="/forgot-password" className="text-sm text-primary-400 hover:text-primary-300">
            Forgot password?
          </Link>
        </div>

        <button
          type="submit"
          disabled={isLoading}
          className="w-full py-3 bg-primary-600 hover:bg-primary-500 disabled:bg-primary-600/50 text-white font-semibold rounded-lg transition-colors"
        >
          {isLoading ? 'Signing in...' : 'Sign in'}
        </button>
      </form>

      <p className="mt-6 text-center text-gray-400">
        Don't have an account?{' '}
        <Link to="/register" className="text-primary-400 hover:text-primary-300 font-medium">
          Sign up
        </Link>
      </p>
    </div>
  )
}
