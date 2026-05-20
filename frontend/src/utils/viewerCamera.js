import * as THREE from 'three';

const THIN_RATIO = 0.08;

/**
 * enquadra a câmera no objeto; heurística para lâminas finas (thin slice / statistical).
 * viewHint: { geometry_mode, slice_axis, slice_thickness, statistical_2d }
 */
export function fitCameraToObject(camera, controls, root, margin = 1.05, viewHint = null) {
  if (!camera || !controls || !root) return;

  const box = new THREE.Box3().setFromObject(root);
  if (box.isEmpty()) return;

  const size = box.getSize(new THREE.Vector3());
  const center = box.getCenter(new THREE.Vector3());
  const dims = [size.x, size.y, size.z];
  const minDim = Math.min(...dims);
  const maxDim = Math.max(...dims) || 1;
  const ratio = minDim / maxDim;

  let thinAxis = -1;
  if (viewHint?.geometry_mode === 'pseudo_2d_thin_slice' && viewHint?.slice_axis) {
    const ax = String(viewHint.slice_axis).toLowerCase();
    thinAxis = ax === 'x' ? 0 : ax === 'y' ? 1 : 2;
  } else if (viewHint?.geometry_mode === 'pseudo_2d_statistical') {
    thinAxis = 2;
  } else if (ratio < THIN_RATIO) {
    thinAxis = dims.indexOf(minDim);
  }

  if (thinAxis >= 0) {
    const inPlane = maxDim * margin * 1.15;
    const dist = Math.max(inPlane, minDim * 8);
    camera.near = Math.max(minDim * 0.1, 1e-5);
    camera.far = Math.max(maxDim * 300, 10);
    camera.updateProjectionMatrix();
    const pos = center.clone();
    if (thinAxis === 0) pos.x += dist;
    else if (thinAxis === 1) pos.y += dist;
    else pos.z += dist;
    camera.position.copy(pos);
    controls.target.copy(center);
    controls.update();
    return;
  }

  const dist = maxDim * margin;
  camera.near = Math.max(maxDim / 2000, 0.0001);
  camera.far = Math.max(maxDim * 200, 1000);
  camera.updateProjectionMatrix();
  camera.position.set(center.x + dist * 0.7, center.y + dist * 0.55, center.z + dist * 0.7);
  controls.target.copy(center);
  controls.update();
}

export function viewHintFromMeshInfo(info) {
  if (!info || typeof info !== 'object') return null;
  const gm = info.geometry_mode || info.geometryMode;
  if (!gm) return null;
  return {
    geometry_mode: gm,
    slice_axis: info.slice_axis,
    slice_thickness: info.slice_thickness,
    slice_position: info.slice_position,
    porosity_method: info.porosity_method,
    statistical_2d: info.statistical_2d,
  };
}
