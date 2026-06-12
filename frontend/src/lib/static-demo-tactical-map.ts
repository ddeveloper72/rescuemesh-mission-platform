import {
  getTerrainMaps,
  getTerrainPaths,
  getTerrainSectors,
  getWaypoints,
  type TerrainMap,
  type TerrainPath,
  type TerrainSector,
  type Waypoint,
} from './api';
import { getTerrainBinding } from './tactical-map/useCaseTerrainBindings';

interface DemoAgentSummary {
  id: string;
  name: string;
  state: string;
}

interface StaticMapElements {
  root: HTMLElement;
  svg: SVGSVGElement;
  pathsGroup: SVGGElement;
  sectorsGroup: SVGGElement;
  waypointsGroup: SVGGElement;
  agentsGroup: SVGGElement;
  fallbackGroup: SVGGElement | null;
  statusEl: HTMLElement | null;
  coverageEl: HTMLElement | null;
  sourceEl: HTMLElement | null;
}

interface Scaling {
  minX: number;
  minY: number;
  scaleX: number;
  scaleY: number;
  offsetX: number;
  offsetY: number;
}

const SVG_NS = 'http://www.w3.org/2000/svg';
const VIEWBOX_WIDTH = 800;
const VIEWBOX_HEIGHT = 450;
const PADDING = 54;

function normaliseArray<T>(value: T[] | { results?: T[] } | undefined | null): T[] {
  if (!value) return [];
  return Array.isArray(value) ? value : value.results || [];
}

function getElements(root: HTMLElement): StaticMapElements | null {
  const svg = root.querySelector<SVGSVGElement>('[data-static-map-svg]');
  const pathsGroup = root.querySelector<SVGGElement>('[data-static-map-paths]');
  const sectorsGroup = root.querySelector<SVGGElement>('[data-static-map-sectors]');
  const waypointsGroup = root.querySelector<SVGGElement>('[data-static-map-waypoints]');
  const agentsGroup = root.querySelector<SVGGElement>('[data-static-map-agents]');

  if (!svg || !pathsGroup || !sectorsGroup || !waypointsGroup || !agentsGroup) {
    return null;
  }

  return {
    root,
    svg,
    pathsGroup,
    sectorsGroup,
    waypointsGroup,
    agentsGroup,
    fallbackGroup: root.querySelector<SVGGElement>('[data-static-map-fallback]'),
    statusEl: root.querySelector<HTMLElement>('[data-static-map-status]'),
    coverageEl: root.querySelector<HTMLElement>('[data-static-map-coverage]'),
    sourceEl: root.querySelector<HTMLElement>('[data-static-map-source]'),
  };
}

function calculateScaling(sectors: TerrainSector[]): Scaling {
  if (!sectors.length) {
    return { minX: 0, minY: 0, scaleX: 1, scaleY: -1, offsetX: PADDING, offsetY: VIEWBOX_HEIGHT - PADDING };
  }

  let minX = Infinity;
  let maxX = -Infinity;
  let minY = Infinity;
  let maxY = -Infinity;

  for (const sector of sectors) {
    const width = sector.width_m || 8;
    const height = sector.height_m || 8;
    minX = Math.min(minX, sector.x_m);
    maxX = Math.max(maxX, sector.x_m + width);
    minY = Math.min(minY, sector.y_m);
    maxY = Math.max(maxY, sector.y_m + height);
  }

  const dataWidth = Math.max(maxX - minX, 1);
  const dataHeight = Math.max(maxY - minY, 1);
  const availableWidth = VIEWBOX_WIDTH - PADDING * 2;
  const availableHeight = VIEWBOX_HEIGHT - PADDING * 2;
  const scale = Math.min(availableWidth / dataWidth, availableHeight / dataHeight);
  const scaledWidth = dataWidth * scale;
  const scaledHeight = dataHeight * scale;

  return {
    minX,
    minY,
    scaleX: scale,
    scaleY: -scale,
    offsetX: PADDING + (availableWidth - scaledWidth) / 2,
    offsetY: VIEWBOX_HEIGHT - PADDING - (availableHeight - scaledHeight) / 2,
  };
}

function toSvg(xM: number, yM: number, scaling: Scaling): { x: number; y: number } {
  return {
    x: (xM - scaling.minX) * scaling.scaleX + scaling.offsetX,
    y: (yM - scaling.minY) * scaling.scaleY + scaling.offsetY,
  };
}

function sectorCenter(sector: TerrainSector, scaling: Scaling): { x: number; y: number } {
  return toSvg(
    sector.x_m + (sector.width_m || 8) / 2,
    sector.y_m + (sector.height_m || 8) / 2,
    scaling
  );
}

function setText(element: HTMLElement | null, value: string): void {
  if (element) element.textContent = value;
}

function createSvgElement<K extends keyof SVGElementTagNameMap>(
  tagName: K,
  attributes: Record<string, string | number>
): SVGElementTagNameMap[K] {
  const element = document.createElementNS(SVG_NS, tagName);
  for (const [key, value] of Object.entries(attributes)) {
    element.setAttribute(key, String(value));
  }
  return element;
}

function getSectorFill(sector: TerrainSector): string {
  const type = sector.sector_type;
  if (['hull_breach', 'bilge', 'flooded', 'submerged'].includes(type)) return '#0e7490';
  if (['hazard_zone', 'collapse_zone', 'collapse', 'sealed_passage'].includes(type)) return '#7f1d1d';
  if (['artifact_alcove', 'inscription_wall', 'squeeze', 'tight_passage'].includes(type)) return '#5b21b6';
  if (['pipe_corridor', 'tank_chamber', 'confined_space'].includes(type)) return '#92400e';
  return '#0f766e';
}

function renderSectors(elements: StaticMapElements, sectors: TerrainSector[], scaling: Scaling): void {
  elements.sectorsGroup.innerHTML = '';

  for (const sector of sectors) {
    const topLeft = toSvg(sector.x_m, sector.y_m + (sector.height_m || 8), scaling);
    const width = Math.max((sector.width_m || 8) * scaling.scaleX, 8);
    const height = Math.max(Math.abs((sector.height_m || 8) * scaling.scaleY), 8);
    const confidence = Math.round((sector.confidence || 0.75) * 100);

    const rect = createSvgElement('rect', {
      x: topLeft.x,
      y: topLeft.y,
      width,
      height,
      rx: 3,
      fill: getSectorFill(sector),
      'fill-opacity': 0.28 + Math.min(confidence, 100) / 250,
      stroke: '#38bdf8',
      'stroke-opacity': 0.45,
      'stroke-width': 1.2,
    });
    rect.appendChild(createSvgElement('title', {})).textContent = `${sector.label} / confidence ${confidence}%`;
    elements.sectorsGroup.appendChild(rect);

    if (width > 50 && height > 22) {
      const center = sectorCenter(sector, scaling);
      const label = createSvgElement('text', {
        x: center.x,
        y: center.y + 3,
        'text-anchor': 'middle',
        fill: '#dbeafe',
        'font-size': 9,
        'font-weight': 600,
        'pointer-events': 'none',
      });
      label.textContent = sector.label;
      elements.sectorsGroup.appendChild(label);
    }
  }
}

function renderPaths(
  elements: StaticMapElements,
  sectors: TerrainSector[],
  paths: TerrainPath[],
  scaling: Scaling
): void {
  elements.pathsGroup.innerHTML = '';
  const sectorById = new Map(sectors.map(sector => [sector.sector_id, sector]));

  for (const path of paths) {
    const from = sectorById.get(path.from_sector_id);
    const to = sectorById.get(path.to_sector_id);
    if (!from || !to) continue;

    const start = sectorCenter(from, scaling);
    const end = sectorCenter(to, scaling);
    const risk = path.traversal_risk || 'normal';
    const stroke = risk === 'high' || risk === 'severe' ? '#f59e0b' : '#60a5fa';

    const line = createSvgElement('line', {
      x1: start.x,
      y1: start.y,
      x2: end.x,
      y2: end.y,
      stroke,
      'stroke-width': risk === 'high' || risk === 'severe' ? 4 : 3,
      'stroke-opacity': 0.72,
      'stroke-linecap': 'round',
    });
    line.appendChild(createSvgElement('title', {})).textContent = `${path.from_sector_label} to ${path.to_sector_label} / ${path.distance_m} m`;
    elements.pathsGroup.appendChild(line);
  }
}

function renderWaypoints(elements: StaticMapElements, waypoints: Waypoint[], scaling: Scaling): void {
  elements.waypointsGroup.innerHTML = '';
  const sortedWaypoints = [...waypoints].sort((a, b) => (a.sequence || 0) - (b.sequence || 0));

  for (const waypoint of sortedWaypoints) {
    const point = toSvg(waypoint.x_m, waypoint.y_m, scaling);
    const marker = createSvgElement('circle', {
      cx: point.x,
      cy: point.y,
      r: 4,
      fill: '#facc15',
      stroke: '#0f172a',
      'stroke-width': 1.5,
    });
    marker.appendChild(createSvgElement('title', {})).textContent = waypoint.label;
    elements.waypointsGroup.appendChild(marker);
  }
}

function readAgents(root: HTMLElement): DemoAgentSummary[] {
  const script = root.querySelector<HTMLScriptElement>('[data-static-map-agents-data]');
  if (!script?.textContent) return [];

  try {
    return JSON.parse(script.textContent) as DemoAgentSummary[];
  } catch {
    return [];
  }
}

function renderAgents(
  elements: StaticMapElements,
  agents: DemoAgentSummary[],
  sectors: TerrainSector[],
  waypoints: Waypoint[],
  scaling: Scaling
): void {
  elements.agentsGroup.innerHTML = '';
  if (!agents.length || !sectors.length) return;

  const sortedWaypoints = [...waypoints].sort((a, b) => (a.sequence || 0) - (b.sequence || 0));
  const fallbackSectors = sectors.map(sector => sectorCenter(sector, scaling));

  agents.forEach((agent, index) => {
    const waypoint = sortedWaypoints[Math.min(index * 2 + 1, sortedWaypoints.length - 1)];
    const point = waypoint
      ? toSvg(waypoint.x_m, waypoint.y_m, scaling)
      : fallbackSectors[Math.min(index, fallbackSectors.length - 1)];

    const color = agent.state === 'failed' || agent.state === 'abandoned'
      ? '#ef4444'
      : agent.state === 'degraded' || agent.state === 'intermittent'
        ? '#f59e0b'
        : agent.state === 'landed_relay'
          ? '#a855f7'
          : '#34d399';

    elements.agentsGroup.appendChild(createSvgElement('circle', {
      cx: point.x,
      cy: point.y,
      r: 8,
      fill: color,
      stroke: '#0f172a',
      'stroke-width': 3,
    }));

    const label = createSvgElement('text', {
      x: point.x + 12,
      y: point.y - 10,
      fill: '#e2e8f0',
      'font-size': 10,
      'font-weight': 700,
    });
    label.textContent = agent.name;
    elements.agentsGroup.appendChild(label);
  });
}

async function loadTerrainForUseCase(useCase: string): Promise<{
  terrainMap: TerrainMap;
  sectors: TerrainSector[];
  paths: TerrainPath[];
  waypoints: Waypoint[];
} | null> {
  const binding = getTerrainBinding(useCase);
  if (!binding?.terrainMapSlug) return null;

  const [mapsResult, sectorsResult, pathsResult, waypointsResult] = await Promise.all([
    getTerrainMaps(binding.siteSlug),
    getTerrainSectors(binding.terrainMapSlug),
    getTerrainPaths(binding.terrainMapSlug),
    getWaypoints(binding.terrainMapSlug),
  ]);

  const maps = normaliseArray<TerrainMap>(mapsResult.data as any);
  const terrainMap = maps.find(map => map.slug === binding.terrainMapSlug);
  const sectors = normaliseArray<TerrainSector>(sectorsResult.data as any);
  const paths = normaliseArray<TerrainPath>(pathsResult.data as any);
  const waypoints = normaliseArray<Waypoint>(waypointsResult.data as any);

  if (!mapsResult.success || !sectorsResult.success || !terrainMap || !sectors.length) {
    return null;
  }

  return { terrainMap, sectors, paths, waypoints };
}

async function initialiseStaticDemoMap(root: HTMLElement): Promise<void> {
  const elements = getElements(root);
  if (!elements) return;

  const useCase = root.dataset.useCase || '';
  const agents = readAgents(root);
  setText(elements.statusEl, 'Loading seeded terrain...');

  const terrain = await loadTerrainForUseCase(useCase);
  if (!terrain) {
    setText(elements.statusEl, 'Static fallback map');
    setText(elements.sourceEl, 'Fallback profile');
    return;
  }

  const scaling = calculateScaling(terrain.sectors);
  renderPaths(elements, terrain.sectors, terrain.paths, scaling);
  renderSectors(elements, terrain.sectors, scaling);
  renderWaypoints(elements, terrain.waypoints, scaling);
  renderAgents(elements, agents, terrain.sectors, terrain.waypoints, scaling);

  const averageConfidence = terrain.sectors.reduce((sum, sector) => sum + (sector.confidence || 0), 0) / terrain.sectors.length;
  if (elements.fallbackGroup) {
    elements.fallbackGroup.innerHTML = '';
  }
  setText(elements.coverageEl, `${Math.round(averageConfidence * 100)}%`);
  setText(elements.sourceEl, terrain.terrainMap.name);
  setText(elements.statusEl, 'Seeded mission terrain');
}

export function initialiseStaticDemoMaps(): void {
  document.querySelectorAll<HTMLElement>('[data-static-demo-map]').forEach(root => {
    initialiseStaticDemoMap(root).catch(error => {
      console.warn('[StaticDemoMap] Failed to initialise map', error);
      const statusEl = root.querySelector<HTMLElement>('[data-static-map-status]');
      setText(statusEl, 'Static fallback map');
    });
  });
}
