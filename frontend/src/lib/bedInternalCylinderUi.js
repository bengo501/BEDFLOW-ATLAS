/**
 * ui e defaults alinhados a scripts/python_modeling/bed_internal_modes.py
 */

export const ICM_HOLLOW = 'hollow_boolean_applied';
export const ICM_VISIBLE = 'internal_cylinder_visible_no_boolean';
export const ICM_SOLID = 'solid_internal_cylinder_with_particle_holes';

export const ICM_ALL = [ICM_HOLLOW, ICM_VISIBLE, ICM_SOLID];

export function defaultVisibilityForMode(mode) {
  const m = mode || ICM_HOLLOW;
  if (m === ICM_VISIBLE) {
    return {
      show_outer_cylinder: true,
      show_internal_cylinder: true,
      show_particles: true,
      show_boolean_tools: false,
      export_boolean_tools: false,
    };
  }
  if (m === ICM_SOLID) {
    return {
      show_outer_cylinder: true,
      show_internal_cylinder: true,
      show_particles: false,
      show_boolean_tools: false,
      export_boolean_tools: false,
    };
  }
  return {
    show_outer_cylinder: true,
    show_internal_cylinder: false,
    show_particles: true,
    show_boolean_tools: false,
    export_boolean_tools: false,
  };
}

/** ao mudar o modo, sincroniza núcleo; preserva escolhas do utilizador em casco/partículas. */
export function syncVisibilityOnModeChange(mode, prevVis = {}) {
  const base = defaultVisibilityForMode(mode);
  return {
    ...base,
    show_outer_cylinder:
      prevVis.show_outer_cylinder !== undefined
        ? Boolean(prevVis.show_outer_cylinder)
        : base.show_outer_cylinder,
    show_particles:
      prevVis.show_particles !== undefined
        ? Boolean(prevVis.show_particles)
        : base.show_particles,
    show_boolean_tools: Boolean(prevVis.show_boolean_tools),
    export_boolean_tools: Boolean(prevVis.export_boolean_tools),
  };
}

export function modeIncludesInnerCore(mode) {
  return mode === ICM_VISIBLE || mode === ICM_SOLID;
}

/** checkboxes principais na exportação (sem duplicar o modo do cilindro). */
export const EXPORT_MAIN_VISIBILITY_KEYS = [
  'show_outer_cylinder',
  'show_particles',
];

export function exportMainLabelKey(key) {
  if (key === 'show_outer_cylinder') return 'bedExportOuter';
  if (key === 'show_particles') return 'bedExportParticles';
  return key;
}

export function internalCylinderModeHintKey(mode) {
  if (mode === ICM_VISIBLE) return 'bedIcmHintVisible';
  if (mode === ICM_SOLID) return 'bedIcmHintSolid';
  return 'bedIcmHintHollow';
}

export function internalCylinderExportNoteKey(mode) {
  if (mode === ICM_SOLID) return 'bedExportNoteSolid';
  if (mode === ICM_VISIBLE) return 'bedExportNoteVisible';
  return '';
}
