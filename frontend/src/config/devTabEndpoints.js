/**
 * referência estática para o painel «modo dev» (não substitui documentação openapi).
 * chaves = activeTab em App.jsx
 */
export const TAB_DEV_INFO = {
  dashboard: {
    api: [
      'GET /api/status',
      'GET /api/simulations/summary',
      'GET /api/simulations/recent',
      'GET /api/simulations/{id}',
    ],
    persistence: [
      'simulations',
      'beds',
      'results (leitura agregada)',
    ],
  },
  wizard: {
    api: [
      'POST /api/bed/wizard',
      'POST /api/bed/process',
      'POST /api/bed/parse',
      'POST /api/bed/compile-from-bed',
      'POST /api/bed/template',
      'GET /api/bed/template/default',
      'GET /api/bed/wizard/help/{section}',
    ],
    persistence: [
      'beds (via fluxos integrados)',
      'ficheiros gerados em /files',
    ],
  },
  casos: {
    api: [
      'POST /api/cfd/create',
      'POST /api/cfd/run-from-wizard',
      'POST /api/cfd/create-case',
      'GET /api/cfd/list',
      'GET /api/cfd/status/{simulation_id}',
      'DELETE /api/cfd/{simulation_id}',
      'GET /api/casos/list',
      'GET /api/casos/{nome_caso}/detalhes',
      'POST /api/casos/{nome_caso}/executar',
      'DELETE /api/casos/{nome_caso}',
    ],
    persistence: ['simulations', 'results', 'casos em disco (openfoam)', 'sistema de ficheiros de casos'],
  },
  jobs: {
    api: ['GET /api/jobs', 'GET /api/job/{job_id}'],
    persistence: ['tabela jobs (memória/serviço de filas conforme implementação)'],
  },
  'results-simulations': {
    api: [
      'GET /api/simulations',
      'GET /api/simulations/{id}',
      'GET /api/results/simulation/{simulation_id}',
      'POST /api/simulations',
      'DELETE /api/simulations/{id}',
    ],
    persistence: ['simulations', 'results'],
  },
  'results-models': {
    api: [
      'GET /api/models-3d',
      'GET /api/viewer/meshes',
      'GET /api/files/{file_type}',
    ],
    persistence: ['beds', 'modelos 3d em disco', 'ficheiros em generated/'],
  },
  comparisons: {
    api: ['GET /api/simulations', 'GET /api/results/simulation/{id}'],
    persistence: ['simulations', 'results'],
  },
  templates: {
    api: [
      'GET /api/templates/list',
      'GET /api/templates/{id}',
      'POST /api/templates/save',
      'PUT /api/templates/{id}',
      'DELETE /api/templates/{id}',
    ],
    persistence: ['bed_templates'],
  },
  'templates-saved': {
    api: ['GET /api/templates/list', 'POST /api/templates/{id}/duplicate'],
    persistence: ['bed_templates'],
  },
  database: {
    api: [
      'GET /api/database/panel',
      'POST /api/database/events',
      'GET /api/beds',
      'GET /api/simulations',
      'GET /api/stats/overview',
    ],
    persistence: [
      'beds',
      'simulations',
      'results',
      'admin_panel_events',
    ],
  },
  reports: {
    api: [
      'GET /api/reports',
      'POST /api/reports',
      'PATCH /api/reports/{id}',
      'DELETE /api/reports/{id}',
    ],
    persistence: ['reports', 'report_attachments'],
  },
  profile: {
    api: ['GET /api/users', 'GET /api/profile', 'PATCH /api/profile'],
    persistence: ['user_profiles'],
  },
  settings: {
    api: [
      'GET /api/settings',
      'PATCH /api/settings',
      'POST /api/admin/dev/shutdown (dev, opcional)',
    ],
    persistence: ['app_settings (singleton)', 'user_profiles (idioma)'],
  },
};

export function getDevInfoForTab(tab) {
  return TAB_DEV_INFO[tab] || {
    api: ['(sem mapa para este separador)'],
    persistence: ['(consulte a documentação ou o código da rota)'],
  };
}
