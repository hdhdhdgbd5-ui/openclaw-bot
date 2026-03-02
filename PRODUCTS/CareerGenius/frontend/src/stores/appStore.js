import { create } from 'zustand';
import { persist } from 'zustand/middleware';

const useAppStore = create(
  persist(
    (set, get) => ({
      // User state
      user: null,
      setUser: (user) => set({ user }),
      
      // Resume state
      currentResume: null,
      resumeText: '',
      resumeAnalysis: null,
      setCurrentResume: (resume) => set({ currentResume: resume }),
      setResumeText: (text) => set({ resumeText: text }),
      setResumeAnalysis: (analysis) => set({ resumeAnalysis: analysis }),
      
      // Job matching state
      jobDescription: '',
      jobFitScore: null,
      setJobDescription: (desc) => set({ jobDescription: desc }),
      setJobFitScore: (score) => set({ jobFitScore: score }),
      
      // Applications
      applications: [],
      setApplications: (apps) => set({ applications: apps }),
      addApplication: (app) => set((state) => ({ 
        applications: [...state.applications, app] 
      })),
      updateApplication: (id, updates) => set((state) => ({
        applications: state.applications.map(app => 
          app.id === id ? { ...app, ...updates } : app
        )
      })),
      deleteApplication: (id) => set((state) => ({
        applications: state.applications.filter(app => app.id !== id)
      })),
      
      // UI state
      sidebarOpen: false,
      setSidebarOpen: (open) => set({ sidebarOpen: open }),
      toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
      
      // Clear all
      clearAll: () => set({
        currentResume: null,
        resumeText: '',
        resumeAnalysis: null,
        jobDescription: '',
        jobFitScore: null,
      }),
    }),
    {
      name: 'careergenius-storage',
      partialize: (state) => ({
        user: state.user,
        applications: state.applications,
        resumeText: state.resumeText,
      }),
    }
  )
);

export default useAppStore;
