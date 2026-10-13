"use client"
import * as React from "react"

export const ThemeContext = React.createContext<{isDark: boolean, toggleDark: () => void}>({
  isDark: false,
  toggleDark: () => {},
});

export function useTheme() {
  return React.useContext(ThemeContext);
}

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [isDark, setIsDark] = React.useState(false);

  React.useEffect(() => {
    const storedTheme = typeof window !== 'undefined' ? (localStorage.getItem('firby_theme_v3') || 'light') : 'light';
    // Por defecto modo claro blanco; solo cambia a oscuro si el usuario lo guardó explícitamente como 'dark'
    const isCurrentlyDark = storedTheme === 'dark';
    setIsDark(isCurrentlyDark);
    if (isCurrentlyDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
      try {
        localStorage.setItem('theme_v2', 'light');
        localStorage.setItem('theme', 'light');
        localStorage.setItem('firby_theme_v3', 'light');
      } catch (_) {}
    }
    
    // Observer for external changes
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (mutation.attributeName === 'class') {
          const isCurrentlyDark = document.documentElement.classList.contains('dark');
          setIsDark(isCurrentlyDark);
        }
      });
    });
    observer.observe(document.documentElement, { attributes: true });
    return () => observer.disconnect();
  }, []);

  const toggleDark = () => {
    const newDark = !isDark;
    setIsDark(newDark);
    if (newDark) {
        document.documentElement.classList.add('dark');
        localStorage.setItem('firby_theme_v3', 'dark');
        localStorage.setItem('theme_v2', 'dark');
        localStorage.setItem('theme', 'dark');
    } else {
        document.documentElement.classList.remove('dark');
        localStorage.setItem('firby_theme_v3', 'light');
        localStorage.setItem('theme_v2', 'light');
        localStorage.setItem('theme', 'light');
    }
  };

  return <ThemeContext.Provider value={{ isDark, toggleDark }}>{children}</ThemeContext.Provider>;
}
