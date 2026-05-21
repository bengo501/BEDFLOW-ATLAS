// gramatica para arquivos .bed
grammar Bed;

bedFile: section+ EOF;

section: bedSection
       | lidsSection
       | particlesSection
       | packingSection
       | exportSection
       | cfdSection
       | geometrySection
       | generationSection
       | sliceSection
       | statistical2dSection;

bedSection: 'bed' '{' bedProperty+ '}';
bedProperty: 'diameter' '=' NUMBER UNIT ';'                    # bedDiameter
           | 'height' '=' NUMBER UNIT ';'                      # bedHeight
           | 'wall_thickness' '=' NUMBER UNIT ';'              # bedWallThickness
           | 'clearance' '=' NUMBER UNIT ';'                   # bedClearance
           | 'material' '=' STRING ';'                          # bedMaterial
           | 'roughness' '=' NUMBER UNIT ';'                    # bedRoughness
           | 'internal_cylinder_mode' '=' STRING ';'            # bedInternalCylinderMode
           | 'visibility' '{' visibilityProperty+ '}'           # bedVisibilityBlock
           ;

visibilityProperty: 'show_outer_cylinder' '=' BOOLEAN ';'       # visShowOuter
                  | 'show_internal_cylinder' '=' BOOLEAN ';'    # visShowInternal
                  | 'show_particles' '=' BOOLEAN ';'            # visShowParticles
                  | 'show_boolean_tools' '=' BOOLEAN ';'        # visShowBooleanTools
                  | 'export_boolean_tools' '=' BOOLEAN ';'      # visExportBooleanTools
                  ;

lidsSection: 'lids' '{' lidsProperty+ '}';
lidsProperty: 'top_type' '=' lidType ';'            # lidsTopType
            | 'bottom_type' '=' lidType ';'         # lidsBottomType
            | 'top_thickness' '=' NUMBER UNIT ';'   # lidsTopThickness
            | 'bottom_thickness' '=' NUMBER UNIT ';' # lidsBottomThickness
            | 'seal_clearance' '=' NUMBER UNIT ';'  # lidsSealClearance;

lidType: 'flat' | 'hemispherical' | 'none' | STRING;

particlesSection: 'particles' '{' particlesProperty+ '}';
particlesProperty: 'kind' '=' particleKind ';'          # particlesKind
                 | 'diameter' '=' NUMBER UNIT ';'       # particlesDiameter
                 | 'count' '=' NUMBER ';'               # particlesCount
                 | 'target_porosity' '=' NUMBER ';'     # particlesTargetPorosity
                 | 'density' '=' NUMBER UNIT ';'        # particlesDensity
                 | 'mass' '=' NUMBER UNIT ';'           # particlesMass
                 | 'restitution' '=' NUMBER ';'         # particlesRestitution
                 | 'friction' '=' NUMBER ';'            # particlesFriction
                 | 'rolling_friction' '=' NUMBER ';'    # particlesRollingFriction
                 | 'linear_damping' '=' NUMBER ';'      # particlesLinearDamping
                 | 'angular_damping' '=' NUMBER ';'     # particlesAngularDamping
                 | 'seed' '=' NUMBER ';'                # particlesSeed;

particleKind: 'sphere' | 'cube' | 'cylinder' | STRING;

packingSection: 'packing' '{' packingProperty+ '}';
packingProperty: 'method' '=' packingMethod ';'        # packingMethodProp
               | 'gravity' '=' NUMBER UNIT ';'         # packingGravity
               | 'substeps' '=' NUMBER ';'             # packingSubsteps
               | 'iterations' '=' NUMBER ';'           # packingIterations
               | 'damping' '=' NUMBER ';'              # packingDamping
               | 'rest_velocity' '=' NUMBER UNIT ';'   # packingRestVelocity
               | 'max_time' '=' NUMBER UNIT ';'        # packingMaxTime
               | 'collision_margin' '=' NUMBER UNIT ';' # packingCollisionMargin
               | 'gap' '=' NUMBER UNIT ';'              # packingGap
               | 'random_seed' '=' NUMBER ';'          # packingRandomSeed
               | 'max_placement_attempts' '=' NUMBER ';' # packingMaxAttempts
               | 'strict_validation' '=' BOOLEAN ';'   # packingStrictValidation
               | 'step_x' '=' NUMBER UNIT ';'           # packingStepX
               | 'mesh_segmentos' '=' NUMBER ';'        # packingMeshSegmentos
               | 'sphere_lat' '=' NUMBER ';'            # packingSphereLat
               | 'sphere_lon' '=' NUMBER ';'            # packingSphereLon
               | 'use_legacy_drop' '=' BOOLEAN ';'     # packingUseLegacyDrop
               | 'dem' '{' demProperty+ '}'             # packingDemBlock
               ;

demProperty: 'time_step' '=' NUMBER UNIT ';'             # demTimeStep
           | 'steps' '=' NUMBER ';'                      # demSteps
           | 'gravity' '=' NUMBER UNIT ';'               # demGravity
           | 'stiffness' '=' NUMBER ';'                  # demStiffness
           | 'damping' '=' NUMBER ';'                    # demDamping
           | 'friction' '=' NUMBER ';'                   # demFriction
           | 'restitution' '=' NUMBER ';'               # demRestitution
           | 'settle_threshold' '=' NUMBER UNIT ';'      # demSettleThreshold
           | 'max_velocity_threshold' '=' NUMBER UNIT ';' # demMaxVelocity
           | 'seed' '=' NUMBER ';'                       # demSeed
           ;

packingMethod: 'rigid_body' | STRING;

exportSection: 'export' '{' exportProperty+ '}';
exportProperty: 'formats' '=' '[' formatList ']' ';'   # exportFormats
              | 'units' '=' STRING ';'                 # exportUnits
              | 'scale' '=' NUMBER ';'                 # exportScale
              | 'wall_mode' '=' wallMode ';'           # exportWallMode
              | 'fluid_mode' '=' fluidMode ';'         # exportFluidMode
              | 'manifold_check' '=' BOOLEAN ';'       # exportManifoldCheck
              | 'merge_distance' '=' NUMBER UNIT ';'    # exportMergeDistance
              ;

formatList: STRING (',' STRING)*;
wallMode: 'surface' | 'solid' | STRING;
fluidMode: 'none' | 'cavity' | STRING;

cfdSection: 'cfd' '{' cfdProperty+ '}';
cfdProperty: 'regime' '=' cfdRegime ';'                # cfdRegimeProp
           | 'inlet_velocity' '=' NUMBER UNIT ';'      # cfdInletVelocity
           | 'fluid_density' '=' NUMBER UNIT ';'       # cfdFluidDensity
           | 'fluid_viscosity' '=' NUMBER UNIT ';'     # cfdFluidViscosity
           | 'max_iterations' '=' NUMBER ';'           # cfdMaxIterations
           | 'convergence_criteria' '=' NUMBER ';'     # cfdConvergenceCriteria
           | 'write_fields' '=' BOOLEAN ';'             # cfdWriteFields
           ;

cfdRegime: 'laminar' | 'turbulent_rans' | STRING;

geometrySection: 'geometry' '{' geometryProperty+ '}';
geometryProperty: 'mode' '=' geometryMode ';'         # geometryModeProp
           ;

geometryMode: 'full_3d' | 'pseudo_2d_thin_slice' | 'pseudo_2d_statistical' | STRING;

generationSection: 'generation' '{' generationProperty+ '}';
generationProperty: 'backend' '=' generationBackend ';' # generationBackendProp
           ;

generationBackend: 'python_engine' | 'blender' | STRING;

sliceSection: 'slice' '{' sliceProperty+ '}';
sliceProperty: 'enabled' '=' BOOLEAN ';'               # sliceEnabled
            | 'thickness' '=' NUMBER UNIT ';'          # sliceThickness
            | 'axis' '=' STRING ';'                    # sliceAxis
            | 'position' '=' NUMBER UNIT ';'           # slicePosition
            | 'keep_only_intersecting_particles' '=' BOOLEAN ';' # sliceKeepOnly
            | 'preserve_original_packing' '=' BOOLEAN ';' # slicePreservePacking
            | 'slice_particle_policy' '=' STRING ';' # sliceParticlePolicy
            | 'debug_export_gizmos' '=' BOOLEAN ';' # sliceDebugGizmos
            ;

statistical2dSection: 'statistical_2d' '{' statistical2dProperty+ '}';
statistical2dProperty: 'domain_width' '=' NUMBER UNIT ';'   # statDomainWidth
                      | 'domain_height' '=' NUMBER UNIT ';'   # statDomainHeight
                      | 'target_porosity' '=' NUMBER ';'      # statTargetPorosity
                      | 'tolerance' '=' NUMBER ';'            # statTolerance
                      | 'max_attempts' '=' NUMBER ';'           # statMaxAttempts
                      | 'slice_thickness' '=' NUMBER UNIT ';' # statSliceThickness
                      | 'seed' '=' NUMBER ';'                # statSeed
                      ;

NUMBER: '-'? [0-9]+ ('.' [0-9]+)? ([eE] [+-]? [0-9]+)?;
INTEGER: '-'? [0-9]+;
UNIT: 'm' | 'cm' | 'mm' | 'kg' | 'g' | 's' | 'Pa' | 'N' | 'm/s' | 'kg/m3' | 'Pa.s' | 'm/s2' | 'm/s²';
STRING: '"' (~["\r\n])* '"';
BOOLEAN: 'true' | 'false';

WS: [ \t\r\n]+ -> skip;
COMMENT: '//' ~[\r\n]* -> skip;
BLOCK_COMMENT: '/*' ( ~'*' | '*' ~'/' )* '*/' -> skip;
