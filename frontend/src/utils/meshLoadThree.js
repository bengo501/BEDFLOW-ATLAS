import * as THREE from 'three';
import { STLLoader } from 'three/examples/jsm/loaders/STLLoader.js';
import { OBJLoader } from 'three/examples/jsm/loaders/OBJLoader.js';
import { PLYLoader } from 'three/examples/jsm/loaders/PLYLoader.js';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { viewHintFromMeshInfo } from './viewerCamera';

const THIN_RATIO_ORIENT = 0.08;

const MESH_STD = {
  stl: { color: 0x8b7355, metalness: 0.15, roughness: 0.65 },
  obj: { color: 0x7a9e9f, metalness: 0.12, roughness: 0.7 },
  ply: { color: 0x6b8e8f, metalness: 0.1, roughness: 0.75 },
};

function meshStandardMaterial(kind) {
  const k = MESH_STD[kind] || MESH_STD.stl;
  return new THREE.MeshStandardMaterial({
    color: k.color,
    metalness: k.metalness,
    roughness: k.roughness,
    side: THREE.DoubleSide,
  });
}

/** detecta stl exportado com stride 52 (incompatível com three.js STLLoader). */
export function validateStlBinaryBuffer(buffer) {
  if (!buffer || buffer.byteLength < 84) {
    return { ok: false, message: 'ficheiro stl demasiado pequeno ou vazio' };
  }
  const dv = new DataView(buffer);
  if (String.fromCharCode(dv.getUint8(0), dv.getUint8(1), dv.getUint8(2), dv.getUint8(3), dv.getUint8(4)).toLowerCase() === 'solid') {
    return { ok: true };
  }
  const nTri = dv.getUint32(80, true);
  if (nTri < 1) {
    return { ok: false, message: 'stl binário sem triângulos' };
  }
  const expect50 = 84 + 50 * nTri;
  const expect52 = 84 + 52 * nTri;
  if (buffer.byteLength === expect52 && buffer.byteLength !== expect50) {
    return {
      ok: false,
      message:
        'stl gerado com formato antigo (incompatível com o viewer). regenere o modelo com o motor python atualizado.',
    };
  }
  if (buffer.byteLength < expect50) {
    return { ok: false, message: 'stl truncado ou corrupto' };
  }
  return { ok: true };
}

export function countVertices(obj) {
  let n = 0;
  obj.traverse((ch) => {
    if (ch.isMesh && ch.geometry) {
      const pos = ch.geometry.attributes?.position;
      if (pos) n += pos.count;
    }
  });
  return n;
}

export function orientBedVertical(root, viewHint = null) {
  const gm = viewHint?.geometry_mode;
  if (gm === 'pseudo_2d_thin_slice' || gm === 'pseudo_2d_statistical') {
    return;
  }
  const box = new THREE.Box3().setFromObject(root);
  if (box.isEmpty()) return;
  const size = box.getSize(new THREE.Vector3());
  const dims = [size.x, size.y, size.z];
  const minDim = Math.min(...dims);
  const maxDim = Math.max(...dims) || 1;
  if (minDim / maxDim < THIN_RATIO_ORIENT) {
    return;
  }
  const longest =
    size.x >= size.y && size.x >= size.z ? 'x' : size.y >= size.x && size.y >= size.z ? 'y' : 'z';
  if (longest === 'y') return;
  if (longest === 'x') {
    root.rotation.z = Math.PI / 2;
  } else {
    root.rotation.x = -Math.PI / 2;
  }
  root.updateMatrixWorld(true);
}

export function centerOnFloor(root) {
  const box = new THREE.Box3().setFromObject(root);
  if (box.isEmpty()) return;
  const center = box.getCenter(new THREE.Vector3());
  const minY = box.min.y;
  root.position.x -= center.x;
  root.position.z -= center.z;
  root.position.y -= minY;
}

function applyObjMaterials(root) {
  root.traverse((ch) => {
    if (!ch.isMesh) return;
    const mats = ch.material
      ? Array.isArray(ch.material)
        ? ch.material
        : [ch.material]
      : [];
    const keep = mats.some((m) => m && m.vertexColors);
    if (!keep) {
      ch.material = meshStandardMaterial('obj');
    }
  });
}

export async function parseToObject3D(ext, buffer) {
  const e = (ext || 'stl').toLowerCase().replace(/^\./, '');
  if (e === 'stl') {
    const stlCheck = validateStlBinaryBuffer(buffer);
    if (!stlCheck.ok) {
      throw new Error(stlCheck.message);
    }
    const geom = new STLLoader().parse(buffer);
    geom.computeVertexNormals();
    return new THREE.Mesh(geom, meshStandardMaterial('stl'));
  }
  if (e === 'obj') {
    const text = new TextDecoder('utf-8').decode(buffer);
    const root = new OBJLoader().parse(text);
    applyObjMaterials(root);
    return root;
  }
  if (e === 'ply') {
    const geom = new PLYLoader().parse(buffer);
    geom.computeVertexNormals();
    return new THREE.Mesh(geom, meshStandardMaterial('ply'));
  }
  if (e === 'gltf' || e === 'glb') {
    return new Promise((resolve, reject) => {
      const loader = new GLTFLoader();
      loader.parse(
        buffer,
        '',
        (gltf) => resolve(gltf.scene),
        (err) => reject(err || new Error('gltf parse'))
      );
    });
  }
  throw new Error(`formato nao suportado no viewer: ${e}`);
}

/** carrega buffer, prepara cena (orientação/centro) e devolve objeto three.js. */
export async function loadMeshFromBuffer(buffer, ext, meshInfo = null) {
  const obj = await parseToObject3D(ext, buffer);
  const viewHint = viewHintFromMeshInfo(meshInfo);
  orientBedVertical(obj, viewHint);
  centerOnFloor(obj);
  const verts = countVertices(obj);
  if (verts < 1) {
    throw new Error('malha sem vértices');
  }
  return { object: obj, viewHint, vertices: verts };
}

/** tenta obter sidecar *_pure_bed.json a partir de url /files/.../modelo.stl */
export async function fetchMeshInfoFromFileUrl(fileUrl) {
  if (!fileUrl || typeof fetch !== 'function') return null;
  const m = /^(.*\/)([^/]+)\.(stl|obj|ply)$/i.exec(fileUrl.split('?')[0]);
  if (!m) return null;
  const sidecarUrl = `${m[1]}${m[2]}_pure_bed.json`;
  try {
    const res = await fetch(sidecarUrl);
    if (!res.ok) return null;
    const data = await res.json();
    return {
      geometry_mode: data.geometry_mode,
      slice_axis: data.slice?.slice_axis || data.slice_axis,
      slice_thickness: data.slice?.slice_thickness ?? data.slice_thickness,
      slice_position: data.slice?.slice_position ?? data.slice_position,
      representation_dimension: data.representation_dimension,
      generation_backend: data.generation_backend,
    };
  } catch {
    return null;
  }
}
