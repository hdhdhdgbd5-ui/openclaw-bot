// Score color based on value
export const getScoreColor = (score) => {
  if (score >= 85) return 'text-emerald-500';
  if (score >= 70) return 'text-blue-500';
  if (score >= 50) return 'text-amber-500';
  return 'text-red-500';
};

export const getScoreBg = (score) => {
  if (score >= 85) return 'bg-emerald-500';
  if (score >= 70) return 'bg-blue-500';
  if (score >= 50) return 'bg-amber-500';
  return 'bg-red-500';
};

// Status colors for applications
export const statusColors = {
  applied: 'bg-blue-100 text-blue-800',
  phone_screen: 'bg-purple-100 text-purple-800',
  interview: 'bg-amber-100 text-amber-800',
  final_round: 'bg-orange-100 text-orange-800',
  offer: 'bg-emerald-100 text-emerald-800',
  rejected: 'bg-red-100 text-red-800',
  withdrawn: 'bg-gray-100 text-gray-800',
};

export const statusLabels = {
  applied: 'Applied',
  phone_screen: 'Phone Screen',
  interview: 'Interview',
  final_round: 'Final Round',
  offer: 'Offer Received',
  rejected: 'Rejected',
  withdrawn: 'Withdrawn',
};

// Format date
export const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', { 
    month: 'short', 
    day: 'numeric', 
    year: 'numeric' 
  });
};

// Truncate text
export const truncate = (text, length = 100) => {
  if (!text) return '';
  if (text.length <= length) return text;
  return text.substring(0, length).trim() + '...';
};

// Calculate days ago
export const daysAgo = (dateString) => {
  if (!dateString) return null;
  const date = new Date(dateString);
  const now = new Date();
  const diff = Math.floor((now - date) / (1000 * 60 * 60 * 24));
  return diff;
};

// Download text as file
export const downloadText = (text, filename, type = 'text/plain') => {
  const blob = new Blob([text], { type });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
};

// Copy to clipboard
export const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (err) {
    console.error('Failed to copy:', err);
    return false;
  }
};

// Parse salary range
export const parseSalary = (salaryString) => {
  if (!salaryString) return null;
  const match = salaryString.match(/\$?([\d,]+)/g);
  if (!match) return null;
  return match.map(s => parseInt(s.replace(/,/g, '')));
};

// Word count
export const wordCount = (text) => {
  if (!text) return 0;
  return text.trim().split(/\s+/).length;
};
