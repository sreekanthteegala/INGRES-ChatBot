// Theme definitions
export const themes = {
  light: {
    name: 'Light',
    icon: '☀️',
    colors: {
      bg: 'from-blue-50 to-indigo-50',
      panel: 'bg-white',
      text: 'text-gray-900',
      textSecondary: 'text-gray-600',
      textTertiary: 'text-gray-500',
      border: 'border-gray-200',
      input: 'bg-white border-gray-300 text-gray-900',
      inputFocus: 'focus:ring-blue-500 focus:border-blue-500',
      button: 'bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700',
      buttonSecondary: 'bg-gray-100 hover:bg-gray-200 text-gray-700',
      userMessage: 'bg-gradient-to-r from-blue-500 to-indigo-600 text-white',
      botMessage: 'bg-white border-gray-200 text-gray-900',
      avatar: 'bg-gradient-to-br from-blue-500 to-indigo-600',
      userAvatar: 'bg-gray-200 text-gray-600',
      badge: 'bg-green-50 border-green-200 text-green-700',
      badgeDot: 'bg-green-500',
      listItem: 'bg-blue-50 border-blue-100 hover:bg-blue-100',
      chart: 'bg-gray-50 border-gray-200',
    }
  },
  dark: {
    name: 'Dark',
    icon: '🌙',
    colors: {
      bg: 'from-slate-900 to-slate-800',
      panel: 'bg-slate-800',
      text: 'text-gray-100',
      textSecondary: 'text-gray-300',
      textTertiary: 'text-gray-400',
      border: 'border-slate-700',
      input: 'bg-slate-700 border-slate-600 text-gray-100',
      inputFocus: 'focus:ring-blue-400 focus:border-blue-400',
      button: 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700',
      buttonSecondary: 'bg-slate-700 hover:bg-slate-600 text-gray-200',
      userMessage: 'bg-gradient-to-r from-blue-600 to-purple-600 text-white',
      botMessage: 'bg-slate-700 border-slate-600 text-gray-100',
      avatar: 'bg-gradient-to-br from-blue-600 to-purple-600',
      userAvatar: 'bg-slate-600 text-gray-300',
      badge: 'bg-green-900 border-green-700 text-green-300',
      badgeDot: 'bg-green-400',
      listItem: 'bg-slate-700 border-slate-600 hover:bg-slate-600',
      chart: 'bg-slate-700 border-slate-600',
    }
  },
  ocean: {
    name: 'Ocean',
    icon: '🌊',
    colors: {
      bg: 'from-cyan-50 to-blue-100',
      panel: 'bg-white',
      text: 'text-slate-900',
      textSecondary: 'text-slate-700',
      textTertiary: 'text-slate-500',
      border: 'border-cyan-200',
      input: 'bg-white border-cyan-300 text-slate-900',
      inputFocus: 'focus:ring-cyan-500 focus:border-cyan-500',
      button: 'bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700',
      buttonSecondary: 'bg-cyan-50 hover:bg-cyan-100 text-cyan-900',
      userMessage: 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white',
      botMessage: 'bg-white border-cyan-200 text-slate-900',
      avatar: 'bg-gradient-to-br from-cyan-500 to-blue-600',
      userAvatar: 'bg-cyan-100 text-cyan-700',
      badge: 'bg-teal-50 border-teal-200 text-teal-700',
      badgeDot: 'bg-teal-500',
      listItem: 'bg-cyan-50 border-cyan-200 hover:bg-cyan-100',
      chart: 'bg-cyan-50 border-cyan-200',
    }
  },
  forest: {
    name: 'Forest',
    icon: '🌿',
    colors: {
      bg: 'from-green-50 to-emerald-100',
      panel: 'bg-white',
      text: 'text-gray-900',
      textSecondary: 'text-gray-700',
      textTertiary: 'text-gray-500',
      border: 'border-green-200',
      input: 'bg-white border-green-300 text-gray-900',
      inputFocus: 'focus:ring-green-500 focus:border-green-500',
      button: 'bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700',
      buttonSecondary: 'bg-green-50 hover:bg-green-100 text-green-900',
      userMessage: 'bg-gradient-to-r from-green-600 to-emerald-600 text-white',
      botMessage: 'bg-white border-green-200 text-gray-900',
      avatar: 'bg-gradient-to-br from-green-600 to-emerald-600',
      userAvatar: 'bg-green-100 text-green-700',
      badge: 'bg-lime-50 border-lime-200 text-lime-700',
      badgeDot: 'bg-lime-500',
      listItem: 'bg-green-50 border-green-200 hover:bg-green-100',
      chart: 'bg-green-50 border-green-200',
    }
  }
}

export const getTheme = (themeName) => {
  return themes[themeName] || themes.light
}

export const saveTheme = (themeName) => {
  localStorage.setItem('ingres-theme', themeName)
}

export const loadTheme = () => {
  return localStorage.getItem('ingres-theme') || 'light'
}
