import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  LayoutDashboard, Plus, Trash2, Edit2, Calendar, Building2,
  Briefcase, Clock, CheckCircle2, XCircle, TrendingUp,
  Bell, Filter, Search
} from 'lucide-react';
import toast from 'react-hot-toast';
import axios from 'axios';
import { format, parseISO } from 'date-fns';
import { statusColors, statusLabels, formatDate } from '../utils/helpers';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:3001/api';

const statuses = [
  { value: 'applied', label: 'Applied' },
  { value: 'phone_screen', label: 'Phone Screen' },
  { value: 'interview', label: 'Interview' },
  { value: 'final_round', label: 'Final Round' },
  { value: 'offer', label: 'Offer' },
  { value: 'rejected', label: 'Rejected' },
  { value: 'withdrawn', label: 'Withdrawn' },
];

function ApplicationTracker() {
  const [applications, setApplications] = useState([]);
  const [stats, setStats] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [filter, setFilter] = useState('all');
  const [search, setSearch] = useState('');
  
  const [formData, setFormData] = useState({
    company: '',
    role: '',
    location: '',
    appliedDate: format(new Date(), 'yyyy-MM-dd'),
    status: 'applied',
    salary: '',
    notes: '',
    url: '',
    followUpDate: '',
  });

  useEffect(() => {
    fetchApplications();
    fetchStats();
  }, []);

  const fetchApplications = async () => {
    try {
      const response = await axios.get(`${API_URL}/applications`);
      setApplications(response.data);
    } catch (error) {
      console.error('Error fetching applications:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API_URL}/applications/stats/dashboard`);
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingId) {
        await axios.put(`${API_URL}/applications/${editingId}`, formData);
        toast.success('Application updated!');
      } else {
        await axios.post(`${API_URL}/applications`, formData);
        toast.success('Application added!');
      }
      setShowForm(false);
      setEditingId(null);
      resetForm();
      fetchApplications();
      fetchStats();
    } catch (error) {
      toast.error('Failed to save application');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this application?')) return;
    try {
      await axios.delete(`${API_URL}/applications/${id}`);
      toast.success('Application deleted');
      fetchApplications();
      fetchStats();
    } catch (error) {
      toast.error('Failed to delete');
    }
  };

  const handleEdit = (app) => {
    setFormData({
      company: app.company,
      role: app.role,
      location: app.location || '',
      appliedDate: app.appliedDate?.split('T')[0] || format(new Date(), 'yyyy-MM-dd'),
      status: app.status,
      salary: app.salary || '',
      notes: app.notes || '',
      url: app.url || '',
      followUpDate: app.followUpDate?.split('T')[0] || '',
    });
    setEditingId(app.id);
    setShowForm(true);
  };

  const resetForm = () => {
    setFormData({
      company: '',
      role: '',
      location: '',
      appliedDate: format(new Date(), 'yyyy-MM-dd'),
      status: 'applied',
      salary: '',
      notes: '',
      url: '',
      followUpDate: '',
    });
  };

  const filteredApplications = applications.filter(app => {
    const matchesFilter = filter === 'all' || app.status === filter;
    const matchesSearch = 
      app.company?.toLowerCase().includes(search.toLowerCase()) ||
      app.role?.toLowerCase().includes(search.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900 mb-2">Application Tracker</h1>
        <p className="text-slate-600">Track your job search progress and stay organized</p>
      </div>

      {/* Stats Dashboard */}
      <{stats && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8"
        >
          <div className="bg-white rounded-2xl border border-slate-200 p-4">
            <p className="text-sm text-slate-500">Total Applications</p>
            <p className="text-3xl font-bold text-slate-900">{stats.total}</p>
          </div>
          
          <div className="bg-white rounded-2xl border border-slate-200 p-4">
            <p className="text-sm text-slate-500">Interview Rate</p>
            <p className="text-3xl font-bold text-emerald-600">{stats.interviewRate}%</p>
          </div>
          
          <div className="bg-white rounded-2xl border border-slate-200 p-4">
            <p className="text-sm text-slate-500">This Month</p>
            <p className="text-3xl font-bold text-primary-600">{stats.thisMonth}</p>
          </div>
          
          <div className="bg-white rounded-2xl border border-slate-200 p-4">
            <p className="text-sm text-slate-500">Avg Response Time</p>
            <p className="text-3xl font-bold text-slate-900">
              {stats.averageResponseTime ? `${stats.averageResponseTime}d` : 'N/A'}
            </p>
          </div>
        </motion.div>
      )}

      {/* Add Button & Filters */}
      <div className="flex flex-col md:flex-row gap-4 mb-6">
        <button
          onClick={() => {
            setShowForm(!showForm);
            if (showForm) {
              setEditingId(null);
              resetForm();
            }
          }}
          className="flex items-center justify-center gap-2 px-6 py-3 bg-primary-600 text-white rounded-xl font-medium hover:bg-primary-700"
        >
          {showForm ? <XCircle className="w-5 h-5" /> : <Plus className="w-5 h-5" />}
          {showForm ? 'Cancel' : 'Add Application'}
        </button>

        <div className="flex-1 flex gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search companies or roles..."
              className="w-full pl-10 pr-4 py-3 border border-slate-300 rounded-xl focus:ring-2 focus:ring-primary-500"
            />
          </div>

          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="px-4 py-3 border border-slate-300 rounded-xl focus:ring-2 focus:ring-primary-500"
          >
            <option value="all">All Statuses</option>
            {statuses.map(s => (
              <option key={s.value} value={s.value}>{s.label}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Add/Edit Form */}
      <{showForm && (
        <motion.form
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          onSubmit={handleSubmit}
          className="bg-white rounded-2xl border border-slate-200 p-6 mb-6"
        >
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Company *</label>
              <input
                type="text"
                required
                value={formData.company}
                onChange={(e) => setFormData({ ...formData, company: e.target.value })}
                className="w-full p-3 border border-slate-300 rounded-xl focus:ring-2 focus:ring-primary-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Role *</label>
              <input
                type="text"
                required
                value={formData.role}
                onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                className="w-full p-3 border border-slate-300 rounded-xl focus:ring-2 focus:ring-primary-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Location</label>
              <input
                type="text"
                value={formData.location}
                onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                className="w-full p-3 border border-slate-300 rounded-xl focus:ring-2 focus:ring-primary-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Salary Range</label>
              <input
                type="text"
                value={formData.salary}
                onChange={(e) => setFormData({ ...formData, salary: e.target.value })}
                placeholder="e.g., $80k-$100k"
                className="w-full p-3 border border-slate-300 rounded-xl focus:ring-2 focus:ring-primary-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Applied Date *</label>
              <input
                type="date"
                required
                value={formData.appliedDate}
                onChange={(e) => setFormData({ ...formData, appliedDate: e.target.value })}
                className="w-full p-3 border border-slate-300 rounded-xl focus:ring-2 focus:ring-primary-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Status</label>
              <select
                value={formData.status}
                onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                className="w-full p-3 border border-slate-300 rounded-xl focus:ring-2 focus:ring-primary-500"
              >
                {statuses.map(s => (
                  <option key={s.value} value={s.value}>{s.label}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Follow-up Date</label>
              <input
                type="date"
                value={formData.followUpDate}
                onChange={(e) => setFormData({ ...formData, followUpDate: e.target.value })}
                className="w-full p-3 border border-slate-300 rounded-xl focus:ring-2 focus:ring-primary-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Job Posting URL</label>
              <input
                type="url"
                value={formData.url}
                onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                className="w-full p-3 border border-slate-300 rounded-xl focus:ring-2 focus:ring-primary-500"
              />
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-slate-700 mb-1">Notes</label>
              <textarea
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                rows={3}
                className="w-full p-3 border border-slate-300 rounded-xl focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>

          <div className="mt-6 flex gap-3">
            <button
              type="submit"
              className="px-6 py-3 bg-primary-600 text-white rounded-xl font-medium hover:bg-primary-700"
            >
              {editingId ? 'Update Application' : 'Save Application'}
            </button>
            
            <button
              type="button"
              onClick={() => {
                setShowForm(false);
                setEditingId(null);
                resetForm();
              }}
              className="px-6 py-3 bg-slate-200 text-slate-700 rounded-xl font-medium hover:bg-slate-300"
            >
              Cancel
            </button>
          </div>
        </motion.form>
      )}

      {/* Applications List */}
      <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden">
        <{filteredApplications.length === 0 ? (
          <div className="p-12 text-center">
            <LayoutDashboard className="w-16 h-16 text-slate-300 mx-auto mb-4" />
            <p className="text-slate-500">No applications found. Start tracking your job search!</p>
          </div>
        ) : (
          <div className="divide-y divide-slate-200">
            {filteredApplications.map((app) => (
              <div key={app.id} className="p-6 hover:bg-slate-50 transition-colors">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold text-slate-900">{app.role}</h3>
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${statusColors[app.status]}`}>
                        {statusLabels[app.status]}
                      </span>
                    </div>
                    
                    <div className="flex items-center gap-4 text-sm text-slate-500">
                      <span className="flex items-center gap-1">
                        <Building2 className="w-4 h-4" />
                        {app.company}
                      </span>
                      
                      <{app.location && (
                        <span className="flex items-center gap-1">
                          <Briefcase className="w-4 h-4" />
                          {app.location}
                        </span>
                      )}
                      
                      <span className="flex items-center gap-1">
                        <Calendar className="w-4 h-4" />
                        Applied {formatDate(app.appliedDate)}
                      </span>
                    </div>
                    
                    <{app.notes && (
                      <p className="mt-2 text-sm text-slate-600">{app.notes}</p>
                    )}
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleEdit(app)}
                      className="p-2 text-slate-500 hover:bg-slate-200 rounded-lg"
                    >
                      <Edit2 className="w-5 h-5" />
                    </button>
                    
                    <button
                      onClick={() => handleDelete(app.id)}
                      className="p-2 text-red-500 hover:bg-red-50 rounded-lg"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default ApplicationTracker;
