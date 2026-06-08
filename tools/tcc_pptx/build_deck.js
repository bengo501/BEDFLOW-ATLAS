// Apresentacao de TCC II — BEDFLOW-ATLAS  (conteudo alinhado ao PDF final)
const pptxgen = require("pptxgenjs");
const path = require("path");
const fs = require("fs");

const IMG = path.join(__dirname, "img");
const OUTDIR = path.join(__dirname, "..", "..", "generated", "apresentacao_tcc");
fs.mkdirSync(OUTDIR, { recursive: true });
const im = (n) => path.join(IMG, n);

// paleta
const NAVY = "1E2761", NAVY2 = "2A356F", ICE = "CADCFC", ORANGE = "E8732A";
const INK = "222A3A", GRAY = "5A6472", CARD = "F4F6FC", LINE = "DCE3F2";
const WHITE = "FFFFFF", GREEN = "1E8E5A", RED = "C0392B", MONOBG = "0D1117";
const HEAD = "Georgia", BODY = "Calibri", MONO = "Consolas";

const p = new pptxgen();
p.defineLayout({ name: "W", width: 13.333, height: 7.5 });
p.layout = "W";
p.author = "Bernardo Klein Heitz";
p.title = "BEDFLOW-ATLAS — TCC II";
const H = 7.5;
const sh = () => ({ type: "outer", color: "1B2440", blur: 9, offset: 3, angle: 135, opacity: 0.18 });

let pageNo = 0;
function chrome(s, opts = {}) {
  s.background = { color: opts.bg || WHITE };
  if (!opts.dark) {
    pageNo++;
    s.addText("BEDFLOW · ATLAS", { x: 0.6, y: 7.06, w: 6, h: 0.3, fontSize: 9, color: GRAY, fontFace: BODY, charSpacing: 2 });
    s.addText(String(pageNo).padStart(2, "0"), { x: 12.3, y: 7.06, w: 0.5, h: 0.3, fontSize: 9, color: GRAY, fontFace: BODY, align: "right" });
  }
}
function head(s, kicker, title, tsize = 28) {
  s.addShape(p.shapes.RECTANGLE, { x: 0.6, y: 0.56, w: 0.16, h: 0.16, fill: { color: ORANGE } });
  s.addText(kicker.toUpperCase(), { x: 0.85, y: 0.5, w: 11.5, h: 0.3, fontSize: 12.5, bold: true, color: ORANGE, fontFace: BODY, charSpacing: 2, margin: 0 });
  s.addText(title, { x: 0.58, y: 0.82, w: 12.2, h: 0.9, fontSize: tsize, bold: true, color: NAVY, fontFace: HEAD, margin: 0 });
}
function card(s, x, y, w, h, fill = WHITE, withShadow = true, radius = 0.08) {
  const o = { x, y, w, h, fill: { color: fill }, line: { color: LINE, width: 1 }, rectRadius: radius };
  if (withShadow) o.shadow = sh();
  s.addShape(p.shapes.ROUNDED_RECTANGLE, o);
}
function frame(s, img, x, y, w, h, pad = 0.1) {
  card(s, x, y, w, h, WHITE, true);
  s.addImage({ path: im(img), x: x + pad, y: y + pad, w: w - 2 * pad, h: h - 2 * pad, sizing: { type: "contain", w: w - 2 * pad, h: h - 2 * pad } });
}
function bullets(s, items, x, y, w, h, opt = {}) {
  s.addText(items.map((t) => ({
    text: t, options: { bullet: { code: "2022", indent: 14 }, breakLine: true, paraSpaceAfter: (opt.gap ?? 9), color: opt.color || INK }
  })), { x, y, w, h, fontSize: opt.size || 15, fontFace: BODY, valign: "top", margin: 0 });
}
function caption(s, t, x, y, w) {
  s.addText(t, { x, y, w, h: 0.35, fontSize: 10.5, italic: true, color: GRAY, fontFace: BODY, align: "center", margin: 0 });
}
function divider(part, title, sub) {
  const s = p.addSlide(); chrome(s, { dark: true, bg: NAVY });
  s.addShape(p.shapes.RECTANGLE, { x: 0, y: 3.05, w: 0.9, h: 0.09, fill: { color: ORANGE } });
  s.addText(part.toUpperCase(), { x: 0.95, y: 2.5, w: 11, h: 0.4, fontSize: 14, bold: true, color: ORANGE, fontFace: BODY, charSpacing: 3, margin: 0 });
  s.addText(title, { x: 0.9, y: 3.25, w: 11.5, h: 1.1, fontSize: 38, bold: true, color: WHITE, fontFace: HEAD, margin: 0 });
  if (sub) s.addText(sub, { x: 0.95, y: 4.4, w: 10.8, h: 0.6, fontSize: 16, color: ICE, fontFace: BODY, margin: 0 });
}

// ===================== S1 CAPA =====================
{
  const s = p.addSlide(); chrome(s, { dark: true, bg: NAVY });
  s.addShape(p.shapes.RECTANGLE, { x: 0, y: 0, w: 0.22, h: H, fill: { color: ORANGE } });
  s.addImage({ path: im("logo_proj.png"), x: 0.95, y: 0.62, w: 1.55, h: 1.27 });
  s.addText("TRABALHO DE CONCLUSÃO II · BACHARELADO EM CIÊNCIA DA COMPUTAÇÃO", { x: 0.95, y: 2.18, w: 11.5, h: 0.3, fontSize: 12.5, bold: true, color: ORANGE, fontFace: BODY, charSpacing: 1.5, margin: 0 });
  s.addText("BEDFLOW-ATLAS", { x: 0.9, y: 2.5, w: 11.8, h: 1.0, fontSize: 56, bold: true, color: WHITE, fontFace: HEAD, margin: 0 });
  s.addText("Automação de geração de leitos empacotados com uso de software em código aberto", { x: 0.95, y: 3.62, w: 11.2, h: 0.8, fontSize: 18, color: ICE, fontFace: BODY, margin: 0 });
  s.addShape(p.shapes.LINE, { x: 0.97, y: 4.7, w: 6.6, h: 0, line: { color: NAVY2, width: 1.5 } });
  s.addText([
    { text: "Autor   ", options: { color: ICE, bold: true } }, { text: "Bernardo Klein Heitz", options: { color: WHITE, breakLine: true } },
    { text: "Orientador   ", options: { color: ICE, bold: true } }, { text: "Prof. Marco Aurélio Souza Mangan", options: { color: WHITE } },
  ], { x: 0.97, y: 4.85, w: 11, h: 0.9, fontSize: 15, fontFace: BODY, paraSpaceAfter: 4, margin: 0 });
  s.addText("PUCRS · Escola Politécnica   |   Porto Alegre · 2026", { x: 0.97, y: 6.45, w: 8, h: 0.3, fontSize: 13, color: ICE, fontFace: BODY, margin: 0 });
  card(s, 11.15, 6.3, 1.55, 0.72, WHITE, true);
  s.addImage({ path: im("logo_pucrs.png"), x: 11.27, y: 6.46, w: 1.31, h: 0.4, sizing: { type: "contain", w: 1.31, h: 0.4 } });
}

// ===================== S2 AGENDA =====================
{
  const s = p.addSlide(); chrome(s); head(s, "Roteiro", "O que será apresentado");
  const items = [
    ["01", "Contexto e problema", "leitos empacotados, CFD e reprodutibilidade"],
    ["02", "Proposta e objetivos", "3 pilares, 8 objetivos específicos"],
    ["03", "A solução em detalhe", "DSL, compilador, motores e corte 3D"],
    ["04", "Reprodutibilidade", "seed, hash e sidecar em ação"],
    ["05", "Interfaces de uso", "web, terminal e visualizador desktop"],
    ["06", "Avaliação e resultados", "critérios, métricas e comparação entre etapas"],
  ];
  const cw = 5.97, chh = 1.32, gx = 0.26, gy = 0.24, x0 = 0.6, y0 = 1.95;
  items.forEach((it, i) => {
    const cx = x0 + (i % 2) * (cw + gx), cy = y0 + Math.floor(i / 2) * (chh + gy);
    card(s, cx, cy, cw, chh, i % 2 ? CARD : WHITE, true);
    s.addText(it[0], { x: cx + 0.22, y: cy + 0.2, w: 1.0, h: 0.9, fontSize: 34, bold: true, color: ORANGE, fontFace: HEAD, valign: "middle", margin: 0 });
    s.addText(it[1], { x: cx + 1.35, y: cy + 0.24, w: cw - 1.6, h: 0.45, fontSize: 16.5, bold: true, color: NAVY, fontFace: BODY, margin: 0 });
    s.addText(it[2], { x: cx + 1.35, y: cy + 0.7, w: cw - 1.6, h: 0.5, fontSize: 12.5, color: GRAY, fontFace: BODY, margin: 0 });
  });
}

// ===================== S3 CONTEXTO =====================
{
  const s = p.addSlide(); chrome(s); head(s, "Contexto & motivação", "Leitos empacotados e o problema da reprodutibilidade");
  bullets(s, [
    "Leitos empacotados são centrais na engenharia química — reatores catalíticos e colunas de absorção.",
    "A CFD prevê queda de pressão (Δp/L), porosidade e escoamento nos espaços intersticiais.",
    "Gerar a geometria 3D do empacotamento depende de ferramentas fragmentadas e operações manuais.",
    "A cada mudança de configuração: editar scripts e converter arquivos → erros e perda de rastreabilidade.",
    "Resultado: dificuldade de auditar, comparar e reproduzir os experimentos.",
  ], 0.7, 1.95, 6.8, 4.6, { size: 15.5, gap: 14 });
  frame(s, "T9_open3d_leito_completo.png", 7.8, 1.95, 4.95, 4.5);
  caption(s, "Leito empacotado gerado e inspecionado na própria plataforma", 7.8, 6.5, 4.95);
}

// ===================== S4 PILARES =====================
{
  const s = p.addSlide(); chrome(s); head(s, "Proposta", "Três pilares do BEDFLOW-ATLAS");
  const pil = [
    ["01", "DSL .bed", "Linguagem declarativa formalizada em ANTLR 4. Descreve o leito de forma padronizada, auditável e agnóstica ao simulador."],
    ["02", "Motores de geração", "Perfis intercambiáveis: Blender 4.x headless (corpo rígido) e Python puro (stdlib), determinístico e portátil."],
    ["03", "Reprodutibilidade", "Hash SHA-256 do params.json identifica cada execução; a seed fixa garante o mesmo arranjo de partículas."],
  ];
  const cw = 3.87, gx = 0.26, x0 = 0.6, y = 2.05, chh = 4.15;
  pil.forEach((c, i) => {
    const x = x0 + i * (cw + gx);
    card(s, x, y, cw, chh, i === 1 ? NAVY : WHITE, true);
    const fg = i === 1 ? WHITE : NAVY, sub = i === 1 ? ICE : INK;
    s.addShape(p.shapes.OVAL, { x: x + 0.3, y: y + 0.35, w: 0.85, h: 0.85, fill: { color: ORANGE } });
    s.addText(c[0], { x: x + 0.3, y: y + 0.35, w: 0.85, h: 0.85, fontSize: 26, bold: true, color: WHITE, fontFace: HEAD, align: "center", valign: "middle", margin: 0 });
    s.addText(c[1], { x: x + 0.32, y: y + 1.4, w: cw - 0.6, h: 0.6, fontSize: 20, bold: true, color: fg, fontFace: HEAD, margin: 0 });
    s.addText(c[2], { x: x + 0.32, y: y + 2.1, w: cw - 0.62, h: 1.9, fontSize: 14, color: sub, fontFace: BODY, margin: 0 });
  });
}

// ===================== S5 OBJETIVOS =====================
{
  const s = p.addSlide(); chrome(s); head(s, "Objetivos", "Objetivo geral e oito objetivos específicos");
  card(s, 0.6, 1.92, 12.13, 1.0, NAVY, true);
  s.addText([{ text: "OBJETIVO GERAL   ", options: { bold: true, color: ORANGE } },
  { text: "projetar e implementar um pipeline automatizado e reprodutível para simulação CFD de leitos empacotados — do problema descrito em linguagem declarativa à geometria 3D e ao caso CFD, sem intervenção manual em múltiplas ferramentas.", options: { color: WHITE } }],
    { x: 0.85, y: 2.06, w: 11.6, h: 0.75, fontSize: 13.5, fontFace: BODY, valign: "middle", margin: 0 });
  const oe = [
    ["OE1", "DSL .bed declarativa"], ["OE2", "Compilador ANTLR4 + hash SHA-256"],
    ["OE3", "Dois motores intercambiáveis"], ["OE4", "Corte 3D→2D (thin slice)"],
    ["OE5", "Interface web"], ["OE6", "CLI Wizard (interativo/headless)"],
    ["OE7", "Rastreabilidade (seed, hash, sidecar)"], ["OE8", "Sistema de templates"],
  ];
  const cw = 2.92, chh = 1.55, gx = 0.13, gy = 0.16, x0 = 0.6, y0 = 3.1;
  oe.forEach((o, i) => {
    const cx = x0 + (i % 4) * (cw + gx), cy = y0 + Math.floor(i / 4) * (chh + gy);
    card(s, cx, cy, cw, chh, CARD, true);
    s.addText(o[0], { x: cx + 0.2, y: cy + 0.22, w: cw - 0.4, h: 0.45, fontSize: 18, bold: true, color: ORANGE, fontFace: HEAD, margin: 0 });
    s.addText(o[1], { x: cx + 0.2, y: cy + 0.72, w: cw - 0.4, h: 0.7, fontSize: 13, color: NAVY, fontFace: BODY, margin: 0 });
  });
  s.addText("Na versão consolidada, OE1–OE8 foram atingidos com evidências verificáveis em código e testes.", { x: 0.6, y: 6.5, w: 12.1, h: 0.35, fontSize: 13, italic: true, color: GRAY, fontFace: BODY, align: "center" });
}

// ===================== S6 TRABALHOS RELACIONADOS =====================
{
  const s = p.addSlide(); chrome(s); head(s, "Trabalhos relacionados", "Workflows da literatura e o posicionamento da proposta");
  const tw = [
    ["Boccardo et al. (2015)", "Blender + Bullet + OpenFOAM; arranjos realistas, mas manual e com alta proficiência exigida."],
    ["Fernengel et al. (2018)", "Scripts Bash/Python + OpenFOAM/ParaView; automatiza, mas exige domínio de várias ferramentas."],
    ["Partopour & Dixon (2017)", "Corpos rígidos (Bullet) + shrink-wrap; malhas de alta qualidade para usuários avançados."],
  ];
  tw.forEach((c, i) => {
    const x = 0.6 + i * 4.05;
    card(s, x, 1.95, 3.85, 1.85, WHITE, true);
    s.addShape(p.shapes.RECTANGLE, { x, y: 1.95, w: 0.1, h: 1.85, fill: { color: GRAY } });
    s.addText(c[0], { x: x + 0.28, y: 2.12, w: 3.4, h: 0.55, fontSize: 14.5, bold: true, color: NAVY, fontFace: HEAD, margin: 0 });
    s.addText(c[1], { x: x + 0.28, y: 2.68, w: 3.45, h: 1.05, fontSize: 12, color: INK, fontFace: BODY, margin: 0 });
  });
  card(s, 0.6, 4.1, 12.13, 2.35, NAVY, true);
  s.addText("LACUNA → CONTRIBUIÇÃO DO BEDFLOW-ATLAS", { x: 0.85, y: 4.3, w: 11.6, h: 0.35, fontSize: 13, bold: true, color: ORANGE, fontFace: BODY, charSpacing: 1.5, margin: 0 });
  s.addText("Os trabalhos resolvem etapas isoladas; falta uma plataforma integrada e rastreável. O BEDFLOW-ATLAS é a solução mais abrangente — única com:", { x: 0.85, y: 4.66, w: 11.6, h: 0.5, fontSize: 14, color: ICE, fontFace: BODY, margin: 0 });
  const tags = ["DSL própria (ANTLR4)", "rastreabilidade por hash + seed", "2 motores (Blender + Python)", "corte 3D→2D paramétrico", "web + CLI + desktop", "código aberto (MIT) + Docker"];
  tags.forEach((t, i) => {
    const x = 0.85 + (i % 3) * 3.85, y = 5.25 + Math.floor(i / 3) * 0.55;
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y, w: 3.6, h: 0.45, fill: { color: NAVY2 }, line: { type: "none" }, rectRadius: 0.22 });
    s.addText("✓ " + t, { x: x + 0.15, y, w: 3.4, h: 0.45, fontSize: 12.5, color: WHITE, fontFace: BODY, valign: "middle", margin: 0 });
  });
}

// ===================== S7 PIPELINE =====================
{
  const s = p.addSlide(); chrome(s); head(s, "Arquitetura", "Pipeline em camadas — do .bed ao caso CFD");
  const steps = [
    ["1", "DSL .bed", "descrição declarativa"],
    ["2", "Compilador ANTLR4", ".bed.json + hash SHA-256"],
    ["3", "Motor de geração", "Blender / Python → STL + sidecar"],
    ["4", "Pipeline OpenFOAM", "blockMesh · snappyHexMesh · simpleFoam"],
    ["5", "API & interfaces", "FastAPI + SQLite · Web/CLI/Desktop"],
  ];
  const n = steps.length, gap = 0.3, cw = (12.13 - gap * (n - 1)) / n, y = 2.75, chh = 2.35;
  steps.forEach((st, i) => {
    const x = 0.6 + i * (cw + gap);
    card(s, x, y, cw, chh, i % 2 ? CARD : WHITE, true);
    s.addShape(p.shapes.OVAL, { x: x + cw / 2 - 0.4, y: y + 0.3, w: 0.8, h: 0.8, fill: { color: NAVY } });
    s.addText(st[0], { x: x + cw / 2 - 0.4, y: y + 0.3, w: 0.8, h: 0.8, fontSize: 26, bold: true, color: WHITE, fontFace: HEAD, align: "center", valign: "middle", margin: 0 });
    s.addText(st[1], { x: x + 0.1, y: y + 1.24, w: cw - 0.2, h: 0.6, fontSize: 13.5, bold: true, color: NAVY, fontFace: BODY, align: "center", margin: 0 });
    s.addText(st[2], { x: x + 0.1, y: y + 1.82, w: cw - 0.2, h: 0.5, fontSize: 10.5, color: GRAY, fontFace: BODY, align: "center", margin: 0 });
    if (i < n - 1) s.addText("→", { x: x + cw - 0.02, y: y + chh / 2 - 0.25, w: gap + 0.04, h: 0.5, fontSize: 20, bold: true, color: ORANGE, align: "center", valign: "middle", margin: 0 });
  });
  s.addText("Cada artefato é rastreado por um hash determinístico, independentemente da interface usada.", { x: 0.6, y: 5.55, w: 12.1, h: 0.4, fontSize: 14, italic: true, color: GRAY, fontFace: BODY, align: "center" });
}

// ===================== divider Parte I =====================
divider("Parte I", "A solução em detalhe", "DSL, compilação, motores de geração e corte 3D→2D");

// ===================== S9 DSL =====================
{
  const s = p.addSlide(); chrome(s); head(s, "DSL · OE1", "Linguagem .bed — 10 seções declarativas");
  s.addText("Bed.g4 (ANTLR 4) cresceu de 6→10 seções e de 100→163 linhas. Aceita unidades físicas (5cm, 0.1 m/s) convertidas para o SI.", { x: 0.7, y: 1.9, w: 5.6, h: 0.7, fontSize: 13.5, color: INK, fontFace: BODY, margin: 0 });
  const sec = [["bed · lids · particles", "geometria do leito, tampas e partículas"], ["packing · export · cfd", "empacotamento, formatos de saída e regime"],
  ["geometry  (novo)", "full_3d, pseudo_2d_thin_slice, statistical"], ["generation  (novo)", "motor: python_engine ou blender"], ["slice  (novo)", "eixo, espessura, posição e raio mínimo"], ["statistical_2d  (novo)", "largura, altura, porosidade alvo e seed"]];
  sec.forEach((it, i) => {
    const y = 2.7 + i * 0.63;
    s.addText(it[0], { x: 0.7, y, w: 2.85, h: 0.5, fontSize: 13, bold: true, color: i >= 2 ? ORANGE : NAVY, fontFace: MONO, valign: "middle", margin: 0 });
    s.addText(it[1], { x: 3.6, y, w: 2.75, h: 0.5, fontSize: 11.5, color: GRAY, fontFace: BODY, valign: "middle", margin: 0 });
  });
  frame(s, "T3_arquivo_bed.png", 6.65, 1.9, 6.1, 4.75);
}

// ===================== S10 COMPILADOR =====================
{
  const s = p.addSlide(); chrome(s); head(s, "Compilação · OE2", "Compilador ANTLR4 → params.json + hash SHA-256");
  frame(s, "T4_compile_ok.png", 0.6, 1.95, 7.1, 2.12);
  frame(s, "T5_compile_erro.png", 0.6, 4.22, 7.1, 2.0);
  bullets(s, [
    "Parsing ANTLR com erros sintáticos indicando linha e token.",
    "Normalização das unidades para o Sistema Internacional (SI).",
    "Aplicação de defaults e canonização (ordena, remove nulos).",
    "Geração do .bed.json e hash SHA-256 em _metadata.hash.",
    "Identidade única e imutável de cada configuração.",
  ], 7.95, 2.0, 4.8, 4.2, { size: 14, gap: 12 });
}

// ===================== S11 MOTORES =====================
{
  const s = p.addSlide(); chrome(s); head(s, "Geração · OE3", "Dois motores, a mesma descrição");
  const cardsdef = [
    ["Motor Blender", "Blender 4.x headless · física de corpo rígido (RBD) · empacotamento realista · cenas .blend.", NAVY],
    ["Motor Python puro", "Somente stdlib (math, struct, random) · hexagonal_3d, DEM e statistical_2d · sem dependências · ideal p/ HPC.", ORANGE],
  ];
  cardsdef.forEach((c, i) => {
    const x = 0.6 + i * 6.16;
    card(s, x, 1.95, 5.97, 2.15, WHITE, true);
    s.addShape(p.shapes.RECTANGLE, { x, y: 1.95, w: 0.12, h: 2.15, fill: { color: c[2] } });
    s.addText(c[0], { x: x + 0.35, y: 2.15, w: 5.4, h: 0.5, fontSize: 20, bold: true, color: NAVY, fontFace: HEAD, margin: 0 });
    s.addText(c[1], { x: x + 0.35, y: 2.72, w: 5.45, h: 1.2, fontSize: 13.5, color: INK, fontFace: BODY, margin: 0 });
  });
  s.addText("PARTÍCULAS: esfera · cubo · cilindro        SAÍDAS: STL · OBJ · BLEND · GLTF", { x: 0.6, y: 4.35, w: 12.1, h: 0.35, fontSize: 13, bold: true, color: GRAY, fontFace: BODY, margin: 0 });
  const modes = [["full_3d", "leito completo em 3D"], ["pseudo_2d_thin_slice", "fatia fina (corte)"], ["pseudo_2d_statistical", "representação estatística"]];
  modes.forEach((m, i) => {
    const x = 0.6 + i * 4.05;
    card(s, x, 4.8, 3.85, 1.4, CARD, true);
    s.addText(m[0], { x: x + 0.2, y: 4.98, w: 3.5, h: 0.4, fontSize: 14.5, bold: true, color: NAVY, fontFace: MONO, margin: 0 });
    s.addText(m[1], { x: x + 0.2, y: 5.42, w: 3.5, h: 0.6, fontSize: 12.5, color: GRAY, fontFace: BODY, margin: 0 });
  });
}

// ===================== S12 GERACAO & CORTE =====================
{
  const s = p.addSlide(); chrome(s); head(s, "Execução · OE4", "Geração e corte 3D→2D (thin slice)");
  frame(s, "T6_geracao_3d.png", 0.6, 1.95, 7.5, 2.05);
  frame(s, "T8_corte_3d.png", 0.6, 4.15, 7.5, 2.1);
  bullets(s, [
    "Progresso por etapa: parâmetros → empacotamento → geometria → exportação STL.",
    "Thin slice (principal inovação técnica): eixo, posição e espessura configuráveis.",
    "Substitui a seção por discos no plano e calcula o raio aparente.",
    "Estima a porosidade 2D — análises pseudo-2D com menor custo.",
    "Algoritmo coberto por 29 funções de teste dedicadas.",
  ], 8.35, 2.0, 4.4, 4.3, { size: 14, gap: 11 });
}

// ===================== S13 ARTEFATOS =====================
{
  const s = p.addSlide(); chrome(s); head(s, "Rastreabilidade · OE7", "Artefatos de cada execução");
  frame(s, "T7_arvore_artefatos.png", 0.6, 1.95, 7.4, 3.0);
  bullets(s, [
    "Cada geração produz um conjunto completo de artefatos.",
    ".bed (DSL) · params.json (canônico) · STL e OBJ (malha).",
    "Sidecar JSON: geometry_mode, seed, hash, porosidade e tempo.",
    "Relatório de empacotamento (aceitação, colisões, validação).",
    "Gravados em local_data/models_3d/ — auditáveis e reproduzíveis.",
  ], 0.7, 5.2, 12.0, 1.6, { size: 14.5, gap: 7 });
}

// ===================== divider Parte II =====================
divider("Parte II", "Reprodutibilidade & resultados", "Determinismo por seed, hash e sidecar JSON");

// ===================== S15 R1 =====================
{
  const s = p.addSlide(); chrome(s); head(s, "Reprodutibilidade", "Mesma seed → mesmo hash, mesma geometria");
  frame(s, "R1a_mesma_seed_hashA.png", 0.6, 1.95, 5.0, 3.45);
  frame(s, "R1b_mesma_seed_hashB.png", 5.75, 1.95, 5.0, 3.45);
  card(s, 11.0, 1.95, 1.75, 3.45, NAVY, true);
  s.addText("seed", { x: 11.0, y: 2.25, w: 1.75, h: 0.3, fontSize: 13, color: ICE, fontFace: BODY, align: "center", margin: 0 });
  s.addText("42", { x: 11.0, y: 2.5, w: 1.75, h: 0.8, fontSize: 46, bold: true, color: WHITE, fontFace: HEAD, align: "center", margin: 0 });
  s.addText("duas execuções", { x: 11.0, y: 3.4, w: 1.75, h: 0.3, fontSize: 11, color: ICE, fontFace: BODY, align: "center", margin: 0 });
  s.addText("✓ hash idêntico", { x: 11.0, y: 3.8, w: 1.75, h: 0.4, fontSize: 14, bold: true, color: "8FF0BE", fontFace: BODY, align: "center", margin: 0 });
  card(s, 0.6, 5.6, 12.13, 1.05, MONOBG, true);
  s.addText([{ text: "hash  ", options: { color: ICE } }, { text: "436a003c82659f9f2fa459e402ad635ccc5609c8785e4a65af75b60aa2b177bd", options: { color: "7EE787" } }],
    { x: 0.85, y: 5.78, w: 11.8, h: 0.4, fontSize: 14, fontFace: MONO, margin: 0 });
  s.addText("test_packing_same_seed_same_centers comprova: mantendo seed e parâmetros, o STL é byte a byte idêntico.", { x: 0.85, y: 6.18, w: 11.6, h: 0.4, fontSize: 12.5, italic: true, color: "AEB9D8", fontFace: BODY, margin: 0 });
}

// ===================== S16 R2 =====================
{
  const s = p.addSlide(); chrome(s); head(s, "Reprodutibilidade", "Seeds diferentes → hashes distintos");
  frame(s, "R2a_seed_diferente_hashA.png", 0.6, 1.95, 5.0, 3.45);
  frame(s, "R2b_seed_diferente_hashB.png", 5.75, 1.95, 5.0, 3.45);
  card(s, 11.0, 1.95, 1.75, 3.45, NAVY, true);
  s.addText("seeds", { x: 11.0, y: 2.3, w: 1.75, h: 0.3, fontSize: 13, color: ICE, fontFace: BODY, align: "center", margin: 0 });
  s.addText("42 / 7", { x: 11.0, y: 2.6, w: 1.75, h: 0.7, fontSize: 30, bold: true, color: WHITE, fontFace: HEAD, align: "center", margin: 0 });
  s.addText("✕ hashes diferentes", { x: 11.0, y: 3.7, w: 1.75, h: 0.6, fontSize: 13, bold: true, color: "FFC9A6", fontFace: BODY, align: "center", margin: 0 });
  card(s, 0.6, 5.6, 12.13, 1.05, MONOBG, true);
  s.addText([{ text: "seed 42  ", options: { color: ICE } }, { text: "436a003c…b177bd", options: { color: "7EE787" } },
  { text: "      seed 7  ", options: { color: ICE } }, { text: "cd628255…fbeae275", options: { color: "FFA657" } }],
    { x: 0.85, y: 5.8, w: 11.8, h: 0.4, fontSize: 15, fontFace: MONO, margin: 0 });
  s.addText("Cada alteração de seed gera um novo hash e um novo registro no histórico, sem sobrescrever resultados.", { x: 0.85, y: 6.2, w: 11.6, h: 0.4, fontSize: 12.5, italic: true, color: "AEB9D8", fontFace: BODY, margin: 0 });
}

// ===================== S17 SIDECAR & EXPORT =====================
{
  const s = p.addSlide(); chrome(s); head(s, "Metadados & entrega", "Sidecar JSON e exportação para solvers externos");
  frame(s, "R3_sidecar_json.png", 0.6, 1.95, 6.2, 3.2);
  frame(s, "R4_download_stl.png", 7.0, 1.95, 5.7, 3.2);
  bullets(s, [
    "O sidecar registra geometry_mode, seed, hash SHA-256, porosidade e tempo.",
    "Cada malha pode ser auditada, comparada e reproduzida fora da interface gráfica.",
    "Download do STL pelo dashboard, com confirmação do hash do arquivo.",
    "Pronto para uso em OpenFOAM, COMSOL e outros solvers de CFD.",
  ], 0.7, 5.35, 12.0, 1.4, { size: 14.5, gap: 7 });
}

// ===================== divider Parte III =====================
divider("Parte III", "Interfaces de uso", "Web, terminal (headless) e visualizador desktop");

// ===================== S19 WEB dashboard & wizard =====================
{
  const s = p.addSlide(); chrome(s); head(s, "Interface web · OE5", "Dashboard e assistente de criação");
  frame(s, "W1_dashboard.png", 0.6, 1.95, 6.05, 3.7);
  frame(s, "W2_wizard_geometria.png", 6.85, 1.95, 5.88, 3.7);
  caption(s, "Dashboard: métricas e histórico de simulações", 0.6, 5.72, 6.05);
  caption(s, "Wizard: geometria, partículas, empacotamento e motor", 6.85, 5.72, 5.88);
  s.addText("React + Vite + Three.js · criação por formulário · jobs assíncronos · visualização 3D integrada.", { x: 0.7, y: 6.2, w: 12, h: 0.4, fontSize: 13.5, color: INK, fontFace: BODY, align: "center", margin: 0 });
}

// ===================== S20 WEB viewer & history =====================
{
  const s = p.addSlide(); chrome(s); head(s, "Interface web", "Visualização 3D, jobs e detalhe de execução");
  frame(s, "W8_visualizador_3d.png", 0.6, 1.95, 6.05, 3.95);
  frame(s, "W11_detalhe_execucao.png", 6.85, 1.95, 5.88, 3.95);
  caption(s, "Visualizador 3D no navegador (Three.js) com corte e metadados", 0.6, 6.0, 6.05);
  caption(s, "Histórico e detalhe completo de cada execução (hash, seed, porosidade)", 6.85, 6.0, 5.88);
}

// ===================== S21 WEB admin grid =====================
{
  const s = p.addSlide(); chrome(s); head(s, "Interface web · OE8", "Persistência, relatórios e administração");
  const g = [["W12_banco_de_dados.png", "Banco de dados"], ["W13_relatorios.png", "Relatórios"], ["W10_monitoramento_jobs.png", "Jobs / histórico"], ["W15_perfil.png", "Perfil & templates"]];
  const cw = 5.95, chh = 2.05, gx = 0.23, x0 = 0.6, y0 = 1.95;
  g.forEach((it, i) => {
    const cx = x0 + (i % 2) * (cw + gx), cy = y0 + Math.floor(i / 2) * (chh + 0.55);
    frame(s, it[0], cx, cy, cw, chh);
    s.addText(it[1], { x: cx, y: cy + chh + 0.02, w: cw, h: 0.3, fontSize: 12.5, bold: true, color: NAVY, fontFace: BODY, align: "center", margin: 0 });
  });
}

// ===================== S22 TERMINAL =====================
{
  const s = p.addSlide(); chrome(s); head(s, "Fluxo via terminal · OE6", "CLI Wizard (Typer + Rich) para ambientes headless");
  frame(s, "T1_menu_principal.png", 0.6, 1.95, 5.7, 4.4);
  frame(s, "T2_wizard_interativo.png", 6.5, 1.95, 4.0, 4.4);
  bullets(s, [
    "Iniciado por python bed_wizard.py.",
    "Menu principal Rich, numerado e com destaque visual.",
    "Modo interativo guia o preenchimento por perguntas/respostas.",
    "Modo headless (--no-prompt) para automação em scripts.",
    "Mesma lógica e motor do fluxo web.",
  ], 10.65, 2.1, 2.55, 4.2, { size: 12.5, gap: 11 });
}

// ===================== S23 ARQUITETURA TECNICA =====================
{
  const s = p.addSlide(); chrome(s); head(s, "Implementação", "13 módulos e a stack do sistema");
  const items = [
    ["DSL & Compilador", "Bed.g4 (ANTLR4) · params.json · SHA-256"],
    ["Motores de geração", "Blender 4.x (RBD) · Python puro (stdlib)"],
    ["Corte fino & modos", "thin_slice_*.py · geometry_modes.py"],
    ["Pipeline OpenFOAM", "blockMesh · snappyHexMesh · simpleFoam"],
    ["API & persistência", "FastAPI · SQLAlchemy · SQLite (Postgres/MinIO)"],
    ["Interfaces & jobs", "React/Vite/Three.js · CLI Typer · Open3D"],
  ];
  const cw = 3.87, chh = 1.5, gx = 0.26, gy = 0.3, x0 = 0.6, y0 = 2.0;
  items.forEach((it, i) => {
    const cx = x0 + (i % 3) * (cw + gx), cy = y0 + Math.floor(i / 3) * (chh + gy);
    card(s, cx, cy, cw, chh, i % 2 ? CARD : WHITE, true);
    s.addShape(p.shapes.RECTANGLE, { x: cx, y: cy, w: 0.1, h: chh, fill: { color: ORANGE } });
    s.addText(it[0], { x: cx + 0.3, y: cy + 0.2, w: cw - 0.5, h: 0.4, fontSize: 15.5, bold: true, color: NAVY, fontFace: HEAD, margin: 0 });
    s.addText(it[1], { x: cx + 0.3, y: cy + 0.66, w: cw - 0.5, h: 0.7, fontSize: 12.5, color: INK, fontFace: BODY, margin: 0 });
  });
  s.addText("Arquitetura modular em camadas · contêineres Docker Compose · web, CLI e desktop sobre o mesmo núcleo.", { x: 0.6, y: 6.05, w: 12.1, h: 0.4, fontSize: 13.5, italic: true, color: GRAY, fontFace: BODY, align: "center" });
}

// ===================== divider Parte IV =====================
divider("Parte IV", "Avaliação", "Critérios de aceitação, métricas e comparação entre etapas");

// ===================== S25 REQUISITOS & CRITERIOS =====================
{
  const s = p.addSlide(); chrome(s); head(s, "Avaliação", "Critérios de aceitação atendidos");
  card(s, 0.6, 2.0, 3.55, 4.3, NAVY, true);
  s.addText("15 / 16", { x: 0.6, y: 2.55, w: 3.55, h: 1.0, fontSize: 56, bold: true, color: WHITE, fontFace: HEAD, align: "center", margin: 0 });
  s.addText("critérios de aceitação\natendidos e verificados", { x: 0.7, y: 3.6, w: 3.35, h: 0.8, fontSize: 14, color: ICE, fontFace: BODY, align: "center", margin: 0 });
  s.addText("Pendente: CA16 — execução\ncompleta do solver OpenFOAM\n(curvas Δp/L)", { x: 0.7, y: 4.7, w: 3.35, h: 1.1, fontSize: 12.5, color: "FFC9A6", fontFace: BODY, align: "center", margin: 0 });
  const dims = [
    "Compilação da DSL sem erro + params.json canônico",
    "Hash SHA-256 determinístico por configuração",
    "Seed fixa reproduz o empacotamento (test_packing_seed)",
    "Motores Blender e Python puro geram STL válido",
    "Corte 3D→2D gera discos no plano (test_discs_not_columns)",
    "Porosidade 2D calculada no sidecar",
    "Visualizador abre o modelo (web e desktop)",
    "CLI headless gera STL · Templates CRUD · suíte pytest verde",
  ];
  card(s, 4.35, 2.0, 8.38, 4.3, WHITE, true);
  bullets(s, dims, 4.6, 2.25, 7.9, 3.9, { size: 14, gap: 11, color: INK });
}

// ===================== S26 RESULTADOS QUANTITATIVOS =====================
{
  const s = p.addSlide(); chrome(s); head(s, "Resultados", "Evidências quantitativas");
  const stats = [["4,5", "DSL .bed (0–5)"], ["5,0", "mensagens do compilador"], ["4,8", "dashboard web"], ["27", "arquivos de teste"]];
  const cw = 2.92, x0 = 0.6, y = 2.0, gx = 0.13;
  stats.forEach((st, i) => {
    const x = x0 + i * (cw + gx);
    card(s, x, y, cw, 1.5, i % 2 ? CARD : WHITE, true);
    s.addText(st[0], { x, y: y + 0.22, w: cw, h: 0.7, fontSize: 36, bold: true, color: ORANGE, fontFace: HEAD, align: "center", margin: 0 });
    s.addText(st[1], { x: x + 0.1, y: y + 0.98, w: cw - 0.2, h: 0.4, fontSize: 12, color: GRAY, fontFace: BODY, align: "center", margin: 0 });
  });
  card(s, 0.6, 3.75, 5.97, 2.6, WHITE, true);
  s.addText("Conjunto G4 · 6 execuções", { x: 0.85, y: 3.92, w: 5.5, h: 0.4, fontSize: 15, bold: true, color: NAVY, fontFace: HEAD, margin: 0 });
  bullets(s, [
    "Tempo total por caso: 74–87 s.",
    "Compilação 11–13 s · geração 18–22 s.",
    "Malha 7–9 s · solver 37–43 s.",
    "Hash único gerado em todas as execuções.",
  ], 0.85, 4.4, 5.5, 1.8, { size: 13.5, gap: 9, color: INK });
  card(s, 6.76, 3.75, 5.97, 2.6, NAVY, true);
  s.addText("Repositório (auditável)", { x: 7.0, y: 3.92, w: 5.5, h: 0.4, fontSize: 15, bold: true, color: ORANGE, fontFace: HEAD, margin: 0 });
  bullets(s, [
    "57 commits · tags v0.5.x · PR #101 (1ª avaliação).",
    "27 arquivos de teste (pytest), 29 funções para o corte 2D.",
    "19 templates de configuração reutilizáveis.",
    "Sidecar JSON por STL em local_data/models_3d/.",
  ], 7.0, 4.4, 5.5, 1.8, { size: 13.5, gap: 9, color: WHITE });
}

// ===================== S27 COMPARACAO ETAPAS =====================
{
  const s = p.addSlide(); chrome(s); head(s, "Comparação", "Da primeira etapa à versão consolidada");
  const rows = [
    ["Motor de geração", "Blender (dependência externa)", "Blender + Python puro intercambiáveis"],
    ["Interface CLI", "não existia", "CLI Wizard (interativo + headless)"],
    ["Corte geométrico", "não existia", "thin slice paramétrico 3D→2D"],
    ["Visualizador", "Web 3D básico", "Web 3D + visualizador desktop"],
    ["Cobertura de testes", "6 arquivos", "27 arquivos (+29 funções de corte)"],
    ["Rastreabilidade", "hash SHA-256", "hash + seed + sidecar JSON"],
  ];
  const x0 = 0.6, y0 = 1.9, wC = 3.4, wA = 4.2, wB = 4.53, rh = 0.66;
  s.addText("CAPACIDADE", { x: x0 + 0.1, y: y0, w: wC, h: 0.4, fontSize: 12, bold: true, color: GRAY, fontFace: BODY, charSpacing: 1, margin: 0 });
  s.addText("PRIMEIRA ETAPA", { x: x0 + wC + 0.1, y: y0, w: wA, h: 0.4, fontSize: 12, bold: true, color: GRAY, fontFace: BODY, charSpacing: 1, margin: 0 });
  s.addText("ETAPA ATUAL", { x: x0 + wC + wA + 0.1, y: y0, w: wB, h: 0.4, fontSize: 12, bold: true, color: ORANGE, fontFace: BODY, charSpacing: 1, margin: 0 });
  rows.forEach((r, i) => {
    const y = y0 + 0.5 + i * rh;
    if (i % 2 === 0) s.addShape(p.shapes.RECTANGLE, { x: x0, y, w: wC + wA + wB, h: rh, fill: { color: CARD }, line: { type: "none" } });
    s.addShape(p.shapes.RECTANGLE, { x: x0 + wC + wA, y, w: wB, h: rh, fill: { color: i % 2 ? "EFF3FB" : "E7ECF8" }, line: { type: "none" } });
    s.addText(r[0], { x: x0 + 0.1, y, w: wC - 0.1, h: rh, fontSize: 13.5, bold: true, color: NAVY, fontFace: BODY, valign: "middle", margin: 0 });
    s.addText(r[1], { x: x0 + wC + 0.1, y, w: wA - 0.2, h: rh, fontSize: 13, color: GRAY, fontFace: BODY, valign: "middle", margin: 0 });
    s.addText(r[2], { x: x0 + wC + wA + 0.15, y, w: wB - 0.3, h: rh, fontSize: 13, bold: true, color: NAVY, fontFace: BODY, valign: "middle", margin: 0 });
  });
  s.addText("A versão consolidada respondeu diretamente às fragilidades da 1ª avaliação (edição, visualização, confiança).", { x: 0.6, y: 6.78, w: 12.1, h: 0.35, fontSize: 12.5, italic: true, color: GRAY, fontFace: BODY, align: "center" });
}

// ===================== S28 CONTRIBUICOES & LIMITACOES =====================
{
  const s = p.addSlide(); chrome(s); head(s, "Contribuições & limitações", "O que entrega e o que ainda falta");
  card(s, 0.6, 2.0, 5.97, 4.4, CARD, true);
  s.addText("CONTRIBUIÇÕES", { x: 0.85, y: 2.2, w: 5.5, h: 0.35, fontSize: 14, bold: true, color: GREEN, fontFace: BODY, charSpacing: 1.5, margin: 0 });
  bullets(s, [
    "DSL .bed — descrição padronizada, legível e auditável.",
    "Plataforma aberta integrando geração, rastreabilidade e testes.",
    "Rastreabilidade por seed + hash SHA-256 + sidecar JSON.",
    "Corte 3D→2D (thin slice) — principal inovação técnica.",
  ], 0.85, 2.7, 5.5, 3.4, { size: 14, gap: 13, color: INK });
  card(s, 6.76, 2.0, 5.97, 4.4, NAVY, true);
  s.addText("LIMITAÇÕES", { x: 7.0, y: 2.2, w: 5.5, h: 0.35, fontSize: 14, bold: true, color: "FF9F6B", fontFace: BODY, charSpacing: 1.5, margin: 0 });
  bullets(s, [
    "Execução completa do solver OpenFOAM (curvas Δp/L) pendente.",
    "Perfil rigid_body ainda depende da instalação do Blender.",
    "Fila de jobs opera com um job por vez (sem concorrência).",
    "Pós-processamento CFD depende de ferramentas externas (ParaView).",
  ], 7.0, 2.7, 5.5, 3.4, { size: 14, gap: 13, color: WHITE });
}

// ===================== S29 TRABALHOS FUTUROS =====================
{
  const s = p.addSlide(); chrome(s); head(s, "Perspectivas", "Trabalhos futuros (TF1–TF9)");
  const tf = [
    ["TF1", "Fila multi-slot (Celery + Redis)"], ["TF2", "OpenFOAM no docker-compose"],
    ["TF3", "Pós-processamento automatizado no dashboard"], ["TF4", "Partículas não esféricas (motor Python)"],
    ["TF5", "Validação cruzada da porosidade (tomografia)"], ["TF6", "Expandir a gramática .bed"],
    ["TF7", "Internacionalização completa (i18n)"], ["TF8", "Release/tag da versão consolidada"],
    ["TF9", "Integração programática (COMSOL/Fluent)"],
  ];
  const cw = 3.87, chh = 1.18, gx = 0.26, gy = 0.22, x0 = 0.6, y0 = 2.0;
  tf.forEach((it, i) => {
    const cx = x0 + (i % 3) * (cw + gx), cy = y0 + Math.floor(i / 3) * (chh + gy);
    card(s, cx, cy, cw, chh, i % 2 ? CARD : WHITE, true);
    s.addText(it[0], { x: cx + 0.22, y: cy + 0.2, w: 1.0, h: 0.8, fontSize: 22, bold: true, color: ORANGE, fontFace: HEAD, valign: "middle", margin: 0 });
    s.addText(it[1], { x: cx + 1.2, y: cy + 0.18, w: cw - 1.4, h: 0.85, fontSize: 13, color: NAVY, fontFace: BODY, valign: "middle", margin: 0 });
  });
}

// ===================== S30 CONCLUSAO =====================
{
  const s = p.addSlide(); chrome(s); head(s, "Conclusão", "Síntese do trabalho");
  bullets(s, [
    "O BEDFLOW-ATLAS entrega um pipeline reprodutível do .bed ao caso CFD.",
    "Os oito objetivos específicos (OE1–OE8) foram atingidos com evidências verificáveis.",
    "Reprodutibilidade comprovada: mesma seed → mesmo hash; sidecar audita cada execução.",
    "Dois motores e o corte 3D→2D abstraem a complexidade do usuário.",
    "Evoluiu do protótipo do SIC 2025 a uma plataforma rastreável e extensível.",
  ], 0.7, 2.05, 7.4, 4.3, { size: 16, gap: 15 });
  frame(s, "R3_sidecar_json.png", 8.35, 2.35, 4.4, 2.3);
  card(s, 8.35, 4.95, 4.4, 1.35, NAVY, true);
  s.addText("rastreável · reprodutível · auditável", { x: 8.35, y: 5.3, w: 4.4, h: 0.6, fontSize: 16, bold: true, color: WHITE, fontFace: HEAD, align: "center", valign: "middle", margin: 0 });
}

// ===================== S31 ENCERRAMENTO =====================
{
  const s = p.addSlide(); chrome(s, { dark: true, bg: NAVY });
  s.addShape(p.shapes.RECTANGLE, { x: 0, y: 0, w: 0.22, h: H, fill: { color: ORANGE } });
  s.addImage({ path: im("logo_proj.png"), x: 5.7, y: 1.05, w: 1.95, h: 1.6 });
  s.addText("Obrigado!", { x: 1, y: 3.0, w: 11.3, h: 1.1, fontSize: 54, bold: true, color: WHITE, fontFace: HEAD, align: "center", margin: 0 });
  s.addText("Perguntas são bem-vindas.", { x: 1, y: 4.15, w: 11.3, h: 0.5, fontSize: 19, color: ICE, fontFace: BODY, align: "center", margin: 0 });
  s.addText([
    { text: "Bernardo Klein Heitz", options: { color: WHITE, bold: true, breakLine: true } },
    { text: "Orientador: Prof. Marco Aurélio Souza Mangan", options: { color: ICE, breakLine: true } },
    { text: "github.com/bengo501/BEDFLOW-ATLAS-TCC-2", options: { color: ORANGE } },
  ], { x: 1, y: 5.1, w: 11.3, h: 1.2, fontSize: 14.5, fontFace: BODY, align: "center", paraSpaceAfter: 5, margin: 0 });
}

const OUT = path.join(OUTDIR, "Apresentacao_TCC_BEDFLOW_ATLAS.pptx");
p.writeFile({ fileName: OUT }).then(() => console.log("OK", OUT, "·", pageNo + "+dividers slides"));
