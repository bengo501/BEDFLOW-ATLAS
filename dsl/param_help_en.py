# english strings for bed wizard parameter help (? and help > section menus)
# keys mirror bed_wizard.param_help; only desc and exemplo are localized
from __future__ import annotations

from typing import Dict

PARAM_HELP_EN: Dict[str, Dict[str, str]] = {
    "bed.diameter": {
        "desc": "inner diameter of the cylindrical bed",
        "exemplo": "5 cm bed = 0.05m",
    },
    "bed.height": {
        "desc": "total height of the cylindrical bed",
        "exemplo": "10 cm bed = 0.1m",
    },
    "bed.wall_thickness": {
        "desc": "cylinder wall thickness",
        "exemplo": "2 mm wall = 0.002m",
    },
    "bed.clearance": {
        "desc": "free space above the particle bed",
        "exemplo": "1 cm clearance = 0.01m",
    },
    "bed.material": {
        "desc": "wall material label",
        "exemplo": "steel, aluminum, glass, plastic",
    },
    "bed.roughness": {
        "desc": "inner surface roughness",
        "exemplo": "smooth surface = 0.0m",
    },
    "lids.top_type": {
        "desc": "top lid shape",
        "exemplo": "flat, hemispherical, none (no lid)",
    },
    "lids.bottom_type": {
        "desc": "bottom lid shape",
        "exemplo": "flat, hemispherical, none (no lid)",
    },
    "lids.top_thickness": {
        "desc": "top lid thickness",
        "exemplo": "3 mm lid = 0.003m",
    },
    "lids.bottom_thickness": {
        "desc": "bottom lid thickness",
        "exemplo": "3 mm lid = 0.003m",
    },
    "lids.seal_clearance": {
        "desc": "gap between lid and wall",
        "exemplo": "1 mm gap = 0.001m",
    },
    "particles.kind": {
        "desc": "particle geometry kind",
        "exemplo": "sphere, cube, cylinder",
    },
    "particles.diameter": {
        "desc": "characteristic particle size (sphere: diameter; cube/cylinder: mesh reference)",
        "exemplo": "5 mm particle = 0.005m",
    },
    "particles.count": {
        "desc": "total number of particles",
        "exemplo": "100 particles = faster packing",
    },
    "particles.target_porosity": {
        "desc": "target bed porosity (0-1)",
        "exemplo": "0.4 = 40% void space",
    },
    "particles.density": {
        "desc": "particle material density",
        "exemplo": "glass = 2500 kg/m3, steel = 7850 kg/m3",
    },
    "particles.mass": {
        "desc": "mass per particle",
        "exemplo": "0.0 = computed automatically",
    },
    "particles.restitution": {
        "desc": "restitution (bounce) coefficient",
        "exemplo": "0.0 = no bounce, 1.0 = full bounce",
    },
    "particles.friction": {
        "desc": "friction coefficient between particles",
        "exemplo": "0.5 = moderate friction",
    },
    "particles.rolling_friction": {
        "desc": "rolling resistance",
        "exemplo": "0.1 = rolls easily",
    },
    "particles.linear_damping": {
        "desc": "linear motion damping",
        "exemplo": "0.1 = light damping",
    },
    "particles.angular_damping": {
        "desc": "angular motion damping",
        "exemplo": "0.1 = slight spin resistance",
    },
    "particles.seed": {
        "desc": "random seed for generation",
        "exemplo": "42 = reproducible run",
    },
    "packing.method": {
        "desc": "packing simulation method",
        "exemplo": "rigid_body (physics-based settling)",
    },
    "packing.gravity": {
        "desc": "gravitational acceleration",
        "exemplo": "earth = -9.81 m/s2, moon = -1.62 m/s2",
    },
    "packing.substeps": {
        "desc": "substeps per frame",
        "exemplo": "10 = good accuracy, 50 = high accuracy",
    },
    "packing.iterations": {
        "desc": "solver iterations per substep",
        "exemplo": "10 = good convergence",
    },
    "packing.damping": {
        "desc": "global simulation damping",
        "exemplo": "0.1 = system settles quickly",
    },
    "packing.rest_velocity": {
        "desc": "velocity treated as at rest",
        "exemplo": "0.01 = stopped if below 1 cm/s",
    },
    "packing.max_time": {
        "desc": "maximum simulation time",
        "exemplo": "5.0s = enough for settling",
    },
    "packing.collision_margin": {
        "desc": "collision detection margin",
        "exemplo": "0.001m = 1 mm margin",
    },
    "packing.gap": {
        "desc": "minimum gap between particle surfaces in scientific modes (collision via circumscribed sphere)",
        "exemplo": "0.0001m = 0.1 mm between surfaces",
    },
    "packing.random_seed": {
        "desc": "seed for spherical_packing",
        "exemplo": "7 = reproducible placement",
    },
    "packing.max_placement_attempts": {
        "desc": "max random placement attempts (spherical_packing)",
        "exemplo": "200000",
    },
    "packing.strict_validation": {
        "desc": "if true, fail on invalid geometry or particle count mismatch",
        "exemplo": "true recommended for cfd",
    },
    "packing.step_x": {
        "desc": "horizontal hex grid step (empty = 2*r+gap)",
        "exemplo": "leave empty for automatic",
    },
    "export.formats": {
        "desc": "file formats to export",
        "exemplo": "stl_binary, stl_ascii, obj, blend",
    },
    "export.units": {
        "desc": "export length unit",
        "exemplo": "m, cm, mm",
    },
    "export.scale": {
        "desc": "export scale factor",
        "exemplo": "1.0 = original size, 1000 = mm to m",
    },
    "export.wall_mode": {
        "desc": "wall export mode",
        "exemplo": "surface, solid",
    },
    "export.fluid_mode": {
        "desc": "fluid region export mode",
        "exemplo": "none, cavity",
    },
    "export.manifold_check": {
        "desc": "check mesh is manifold",
        "exemplo": "true = verify mesh integrity",
    },
    "export.merge_distance": {
        "desc": "vertex merge distance",
        "exemplo": "0.001m = merge nearby vertices",
    },
    "cfd.regime": {
        "desc": "fluid flow regime",
        "exemplo": "laminar (low speed), turbulent_rans (high speed)",
    },
    "cfd.inlet_velocity": {
        "desc": "inlet fluid velocity",
        "exemplo": "0.1 m/s = slow flow",
    },
    "cfd.fluid_density": {
        "desc": "fluid density",
        "exemplo": "air = 1.225 kg/m3, water = 1000 kg/m3",
    },
    "cfd.fluid_viscosity": {
        "desc": "dynamic viscosity",
        "exemplo": "air = 1.8e-5 Pa.s, water = 1e-3 Pa.s",
    },
    "cfd.max_iterations": {
        "desc": "maximum solver iterations",
        "exemplo": "1000 = fast run, 10000 = tighter",
    },
    "cfd.convergence_criteria": {
        "desc": "convergence criterion (residual)",
        "exemplo": "1e-6 = good convergence",
    },
    "cfd.write_fields": {
        "desc": "save velocity/pressure fields",
        "exemplo": "true = save results, false = skip",
    },
}
