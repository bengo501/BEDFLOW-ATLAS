// tema visual claro escuro ou seguir o sistema operativo via media query
import { createContext, useContext, useState, useEffect, useCallback } from 'react';

const ThemeContext = createContext();

// le preferencia dark do browser devolve string dark ou light
function getSystemTheme() {
  // match media e api padrao para prefers color scheme
  if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    return 'dark';
  }
  return 'light';
}

// le local storage com migracao de chave antiga theme para theme mode
function readInitialThemeMode() {
  const m = localStorage.getItem('themeMode');
  if (m === 'light' || m === 'dark' || m === 'system') return m;
  const legacy = localStorage.getItem('theme');
  if (legacy === 'light' || legacy === 'dark') return legacy;
  return 'system';
}

// converte modo escolhido pelo utilizador no tema efetivo aplicado ao css
function resolveEffective(mode) {
  if (mode === 'light') return 'light';
  if (mode === 'dark') return 'dark';
  return getSystemTheme();
}

export function ThemeProvider({ children }) {
  // modo pode ser system light dark
  const [themeMode, setThemeModeState] = useState(readInitialThemeMode);
  // tema efetivo light dark ja resolvido
  const [theme, setTheme] = useState(() => resolveEffective(readInitialThemeMode()));

  // quando modo e system escuta mudancas do sistema para atualizar tema
  useEffect(() => {
    const eff = resolveEffective(themeMode);
    setTheme(eff);
    if (themeMode !== 'system') return undefined;
    const mq = window.matchMedia('(prefers-color-scheme: dark)');
    const onChange = () => setTheme(mq.matches ? 'dark' : 'light');
    mq.addEventListener('change', onChange);
    return () => mq.removeEventListener('change', onChange);
  }, [themeMode]);

  // persiste escolha e aplica atributo data theme usado pelas folhas de estilo
  useEffect(() => {
    document.documentElement.classList.add('disable-theme-transition');
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    localStorage.setItem('themeMode', themeMode);
    const id = requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        document.documentElement.classList.remove('disable-theme-transition');
      });
    });
    return () => cancelAnimationFrame(id);
  }, [theme, themeMode]);

  const setThemeMode = useCallback((mode) => {
    if (mode === 'light' || mode === 'dark' || mode === 'system') {
      setThemeModeState(mode);
    }
  }, []);

  const toggleTheme = useCallback(() => {
    setThemeModeState((prev) => {
      if (prev === 'light') return 'dark';
      if (prev === 'dark') return 'light';
      // se estava em system passa para o oposto do sistema atual
      return getSystemTheme() === 'dark' ? 'light' : 'dark';
    });
  }, []);

  const isDarkMode = theme === 'dark';

  return (
    <ThemeContext.Provider
      value={{ theme, themeMode, setThemeMode, toggleTheme, isDarkMode }}
    >
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}
