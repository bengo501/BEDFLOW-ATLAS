/**
 * parâmetros partilhados entre PipelineCompleto (curto), PipelineCompletoFull e BedWizard.
 */

export function modelingProfileFromBackend(generationBackend) {
  const gb = String(generationBackend || '').toLowerCase();
  if (gb.includes('python') || gb === 'pure_python') return 'python';
  return 'blender';
}

export function defaultPipelineCompactParams() {
  return {
    fileName: 'pipeline_leito.bed',
    includeCfd: false,
    diameter: 0.05,
    height: 0.1,
    wall_thickness: 0.002,
    lid_top: 'flat',
    lid_bottom: 'flat',
    lid_thickness: 0.003,
    particle_count: 100,
    particle_type: 'sphere',
    particle_diameter: 0.005,
    packing_method: 'rigid_body',
    gravity: -9.81,
    friction: 0.5,
    substeps: 10,
    geometry_mode: 'full_3d',
    generation_backend: 'blender',
    target_porosity: 0.4,
    seed: 42,
    slice: {
      slice_enabled: true,
      slice_thickness: 0.002,
      slice_axis: 'y',
      slice_position: 0,
      keep_only_intersecting_particles: true,
      preserve_original_packing: true,
    },
    statistical_2d: {
      domain_width: 0.05,
      domain_height: 0.1,
      target_porosity: 0.38,
      tolerance: 0.02,
      max_attempts: 30,
      slice_thickness: 0.002,
      seed: 7,
    },
    cfd_regime: 'laminar',
    inlet_velocity: 0.1,
    fluid_density: 1000,
    fluid_viscosity: 0.001,
  };
}

export function buildNestedPipelineBody(p) {
  const packing =
    p.geometry_mode === 'pseudo_2d_statistical'
      ? { method: 'statistical_reconstruction' }
      : {
          method: p.packing_method,
          gravity: p.gravity,
          substeps: p.substeps,
          friction: p.friction,
        };
  const body = {
    bed: {
      diameter: p.diameter,
      height: p.height,
      wall_thickness: p.wall_thickness,
      clearance: 0.01,
      material: 'steel',
    },
    lids: {
      top_type: p.lid_top,
      bottom_type: p.lid_bottom,
      top_thickness: p.lid_thickness,
      bottom_thickness: p.lid_thickness,
    },
    particles: {
      kind: p.particle_type,
      count: p.particle_count,
      diameter: p.particle_diameter,
      target_porosity: p.target_porosity ?? 0.4,
      seed: p.seed ?? 42,
    },
    packing,
    export: { formats: ['stl_binary'], units: 'm' },
    geometry_mode: p.geometry_mode,
    generation_backend: p.generation_backend,
    cfd: {
      regime: p.cfd_regime,
      inlet_velocity: p.inlet_velocity,
      fluid_density: p.fluid_density,
      fluid_viscosity: p.fluid_viscosity,
    },
  };
  if (p.geometry_mode === 'pseudo_2d_thin_slice' && p.slice) {
    body.slice = { ...p.slice, slice_enabled: true };
  }
  if (p.geometry_mode === 'pseudo_2d_statistical' && p.statistical_2d) {
    body.statistical_2d = p.statistical_2d;
  }
  return body;
}

function str(v) {
  if (v === null || v === undefined) return '';
  return String(v);
}

/** formato postBedWizard / WizardParams (campos string como BedWizard). */
export function toBedWizardRequest(p, options = {}) {
  const mode = options.mode || 'pipeline_completo';
  const fileName = p.fileName || options.fileName || 'pipeline_leito.bed';
  const sl = p.slice || {};
  const st = p.statistical_2d || {};

  const params = {
    bed: {
      diameter: str(p.diameter),
      height: str(p.height),
      wall_thickness: str(p.wall_thickness),
      clearance: '0.01',
      material: 'steel',
      roughness: '0.0',
      internal_cylinder_mode: 'hollow_boolean_applied',
    },
    lids: {
      top_type: p.lid_top || 'flat',
      bottom_type: p.lid_bottom || 'flat',
      top_thickness: str(p.lid_thickness),
      bottom_thickness: str(p.lid_thickness),
      seal_clearance: '0.001',
    },
    particles: {
      kind: p.particle_type || 'sphere',
      diameter: str(p.particle_diameter),
      count: str(p.particle_count),
      target_porosity: str(p.target_porosity ?? 0.4),
      density: '2500.0',
      mass: '0.0',
      restitution: '0.3',
      friction: str(p.friction ?? 0.5),
      rolling_friction: '0.1',
      linear_damping: '0.1',
      angular_damping: '0.1',
      seed: str(p.seed ?? 42),
    },
    packing: {
      method:
        p.geometry_mode === 'pseudo_2d_statistical'
          ? 'statistical_reconstruction'
          : p.packing_method || 'rigid_body',
      gravity: str(p.gravity ?? -9.81),
      substeps: str(p.substeps ?? 10),
      iterations: '10',
      damping: '0.1',
      rest_velocity: '0.01',
      max_time: '5.0',
      collision_margin: '0.001',
      gap: '0.0001',
      random_seed: str(p.seed ?? 42),
      max_placement_attempts: '500000',
      strict_validation: true,
    },
    export: {
      formats: ['stl_binary', 'blend'],
      units: 'm',
      scale: '1.0',
      wall_mode: 'surface',
      fluid_mode: 'none',
      manifold_check: true,
      merge_distance: '0.001',
    },
    geometry_mode: p.geometry_mode || 'full_3d',
    generation_backend: p.generation_backend || 'blender',
    slice: null,
    statistical_2d: null,
    cfd: null,
  };

  if (p.geometry_mode === 'pseudo_2d_thin_slice') {
    params.slice = {
      slice_enabled: true,
      slice_thickness: str(sl.slice_thickness ?? 0.002),
      slice_axis: sl.slice_axis || 'y',
      slice_position: str(sl.slice_position ?? 0),
      keep_only_intersecting_particles:
        sl.keep_only_intersecting_particles !== false,
      preserve_original_packing: sl.preserve_original_packing !== false,
    };
  }

  if (p.geometry_mode === 'pseudo_2d_statistical') {
    params.statistical_2d = {
      domain_width: str(st.domain_width ?? p.diameter),
      domain_height: str(st.domain_height ?? p.height),
      target_porosity: str(st.target_porosity ?? 0.38),
      tolerance: str(st.tolerance ?? 0.02),
      max_attempts: str(st.max_attempts ?? 30),
      slice_thickness: str(st.slice_thickness ?? 0.002),
      seed: str(st.seed ?? 7),
    };
    params.generation_backend = 'python_engine';
  }

  if (p.includeCfd) {
    params.cfd = {
      regime: p.cfd_regime || 'laminar',
      inlet_velocity: str(p.inlet_velocity ?? 0.1),
      fluid_density: str(p.fluid_density ?? 1000),
      fluid_viscosity: str(p.fluid_viscosity ?? 0.001),
      max_iterations: '1000',
      convergence_criteria: '1e-6',
      write_fields: false,
    };
  }

  return { mode, fileName, params };
}

export function validatePipelineGeometryBackend(p) {
  if (
    p.geometry_mode === 'pseudo_2d_statistical' &&
    p.generation_backend !== 'python_engine'
  ) {
    return 'pseudo_2d_statistical exige generation_backend python_engine';
  }
  return null;
}
