// contexto react que guarda toggles de interface e aplica timeout do axios quando chegam settings
import { createContext, useCallback, useContext, useMemo, useState } from 'react';
import api, { setApiClientTimeoutMs } from '../services/api';

// valor null ate o provider montar evita uso fora da arvore correta
const AppUiContext = createContext(null);

// provider envolve a app e expoe estado e setters memorizados
export function AppUiProvider({ children }) {
  // simple mode esconde passos avancados no layout
  // inicializa lendo local storage chave app simple mode valor 1 ativa
  const [simpleMode, setSimpleModeState] = useState(
    () => localStorage.getItem('app_simple_mode') === '1'
  );
  // dev mode mostra botoes perigosos ou paineis extras no frontend
  const [devMode, setDevModeState] = useState(
    () => localStorage.getItem('app_dev_mode') === '1'
  );

  // normaliza para boolean grava string1 ou 0 para persistir entre refreshes
  const setSimpleMode = useCallback((value) => {
    const b = !!value;
    setSimpleModeState(b);
    localStorage.setItem('app_simple_mode', b ? '1' : '0');
  }, []);

  const setDevMode = useCallback((value) => {
    const b = !!value;
    setDevModeState(b);
    localStorage.setItem('app_dev_mode', b ? '1' : '0');
  }, []);

  // chamado depois de get settings para alinhar cliente com servidor
  const applySettingsFromApi = useCallback((s) => {
    // ignora payloads que nao sejam objeto
    if (!s || typeof s !== 'object') return;
    // booleans vindos do pydantic atualizam toggles locais
    if (typeof s.simple_mode === 'boolean') {
      setSimpleMode(s.simple_mode);
    }
    if (typeof s.dev_mode === 'boolean') {
      setDevMode(s.dev_mode);
    }
    // timeout do axios em milissegundos vem de segundos no json
    const sec = s.database_ui?.client_timeout_sec;
    if (sec != null) {
      const n = Number(sec);
      // so aceita janela razoavel para nao travar nem ser agressivo demais
      if (Number.isFinite(n) && n >= 5 && n <= 600) {
        setApiClientTimeoutMs(n * 1000);
      }
    }
  }, [setDevMode, setSimpleMode]);

  // memo evita rerenders profundos quando o objeto value seria novo a cada render
  const value = useMemo(
    () => ({
      simpleMode,
      devMode,
      setSimpleMode,
      setDevMode,
      applySettingsFromApi,
    }),
    [applySettingsFromApi, devMode, setDevMode, setSimpleMode, simpleMode]
  );

  return <AppUiContext.Provider value={value}>{children}</AppUiContext.Provider>;
}

// hook que devolve o contexto ou lanca erro claro se faltar provider
export function useAppUi() {
  const ctx = useContext(AppUiContext);
  if (!ctx) {
    throw new Error('useAppUi deve ser usado dentro de AppUiProvider');
  }
  return ctx;
}
