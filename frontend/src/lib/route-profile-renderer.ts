/**
 * Route Profile Renderer
 * 
 * Renders the route profile SVG chart from a RouteProfileViewModel.
 * Shows route distance (X) vs elevation/depth (Y) with agent positions, sectors, and segments.
 */

import type { RouteProfileViewModel, RouteProfilePoint, RouteProfileSegment } from './tactical-map/routeProfileAdapter';

interface RenderConfig {
  containerId: string;
  viewBoxWidth: number;
  viewBoxHeight: number;
  paddingLeft: number;
  paddingRight: number;
  paddingTop: number;
  paddingBottom: number;
}

const DEFAULT_CONFIG: RenderConfig = {
  containerId: 'route-profile',
  viewBoxWidth: 800,
  viewBoxHeight: 280,
  paddingLeft: 60,
  paddingRight: 40,
  paddingTop: 20,
  paddingBottom: 40
};

/**
 * Initialize and render the route profile
 */
export function initializeRouteProfile(
  viewModel: RouteProfileViewModel,
  config: Partial<RenderConfig> = {}
): void {
  const cfg = { ...DEFAULT_CONFIG, ...config };
  
  // Hide loading state
  const loadingEl = document.getElementById(`${cfg.containerId}-loading`);
  if (loadingEl) loadingEl.style.display = 'none';

  // Update summary
  updateSummary(viewModel, cfg);

  // Render profile
  renderProfile(viewModel, cfg);
}

/**
 * Update summary statistics
 */
function updateSummary(viewModel: RouteProfileViewModel, config: RenderConfig): void {
  const { summary } = viewModel;
  
  console.log('[RouteProfile] Updating summary:', summary);

  // Farthest distance
  const farthestEl = document.getElementById(`${config.containerId}-farthest-distance`);
  if (farthestEl && summary.farthestAgentDistanceM !== undefined) {
    farthestEl.textContent = `${summary.farthestAgentDistanceM.toFixed(0)} m`;
  }

  // Max depth
  const depthEl = document.getElementById(`${config.containerId}-max-depth`);
  if (depthEl && summary.maxDepthM !== undefined) {
    depthEl.textContent = summary.maxDepthM > 0 ? `↓ ${summary.maxDepthM.toFixed(0)} m` : '0 m';
  }

  // Return risk
  const returnEl = document.getElementById(`${config.containerId}-return-risk`);
  if (returnEl && summary.returnRisk) {
    const riskColors: Record<string, string> = {
      low: 'text-green-400',
      moderate: 'text-yellow-400',
      high: 'text-red-400',
      critical: 'text-red-500'
    };
    returnEl.textContent = summary.returnRisk.charAt(0).toUpperCase() + summary.returnRisk.slice(1);
    returnEl.className = riskColors[summary.returnRisk] || 'text-slate-400';
  }

  // Contact risk
  const contactEl = document.getElementById(`${config.containerId}-contact-risk`);
  if (contactEl && summary.contactContinuityRisk) {
    const riskColors: Record<string, string> = {
      stable: 'text-green-400',
      watch: 'text-yellow-400',
      high: 'text-orange-400',
      critical: 'text-red-500'
    };
    contactEl.textContent = summary.contactContinuityRisk.charAt(0).toUpperCase() + summary.contactContinuityRisk.slice(1);
    contactEl.className = riskColors[summary.contactContinuityRisk] || 'text-slate-400';
  }

  // Farthest agent detail
  const agentEl = document.getElementById(`${config.containerId}-farthest-agent`);
  if (agentEl && summary.farthestAgentLabel) {
    const depthLabel = summary.farthestAgentDepthM && summary.farthestAgentDepthM > 0 
      ? `, ↓ ${summary.farthestAgentDepthM.toFixed(0)} m` 
      : '';
    agentEl.textContent = `Farthest active agent: ${summary.farthestAgentLabel} — ${summary.farthestAgentDistanceM?.toFixed(0)} m from entrance${depthLabel}`;
    agentEl.classList.remove('hidden');
  }
}

/**
 * Render the profile chart
 */
function renderProfile(viewModel: RouteProfileViewModel, config: RenderConfig): void {
  const { points, segments, maxRouteDistanceM, minZM, maxZM } = viewModel;

  // Calculate scales
  const chartWidth = config.viewBoxWidth - config.paddingLeft - config.paddingRight;
  const chartHeight = config.viewBoxHeight - config.paddingTop - config.paddingBottom;

  const xMax = Math.max(maxRouteDistanceM, 1);
  const xScale = (routeDistanceM: number) => {
    return config.paddingLeft + (routeDistanceM / xMax) * chartWidth;
  };

  const yScale = (zM: number) => {
    const zRange = maxZM - minZM;
    const normalizedZ = (zM - minZM) / (zRange || 1);
    // Invert Y so positive elevation is up, negative depth is down
    return config.paddingTop + chartHeight - (normalizedZ * chartHeight);
  };

  // Render grid
  renderGrid(config, xScale, yScale, xMax, minZM, maxZM, chartHeight);

  // Render reference line (ground level at z=0)
  renderReferenceLine(config, yScale);

  // Render segments
  renderSegments(segments, points, config, xScale, yScale);

  // Render sector points
  renderSectorPoints(points.filter(p => p.type === 'sector' || p.type === 'origin'), config, xScale, yScale);

  // Render agent points
  renderAgentPoints(points.filter(p => p.type === 'agent' || p.type === 'relay'), config, xScale, yScale);

  // Add interactivity
  addTooltipInteractivity(config);
}

/**
 * Render grid lines
 */
function renderGrid(
  config: RenderConfig,
  xScale: (d: number) => number,
  yScale: (z: number) => number,
  maxDistance: number,
  minZ: number,
  maxZ: number,
  chartHeight: number
): void {
  const gridGroup = document.getElementById(`${config.containerId}-grid`);
  if (!gridGroup) return;

  gridGroup.innerHTML = '';
  
  // Calculate chart dimensions within this scope
  const chartWidth = config.viewBoxWidth - config.paddingLeft - config.paddingRight;

  // Vertical grid lines (distance intervals) - adaptive based on mission range
  let distanceInterval: number;
  if (maxDistance <= 150) {
    distanceInterval = 10;  // 10m intervals for short missions (0-150m)
  } else if (maxDistance <= 300) {
    distanceInterval = 20;  // 20m intervals for medium missions (150-300m)
  } else if (maxDistance <= 600) {
    distanceInterval = 50;  // 50m intervals for long missions (300-600m)
  } else {
    distanceInterval = 100; // 100m intervals for very long missions (600m+)
  }
  
  for (let d = 0; d <= maxDistance; d += distanceInterval) {
    const x = xScale(d);
    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    line.setAttribute('x1', x.toString());
    line.setAttribute('y1', config.paddingTop.toString());
    line.setAttribute('x2', x.toString());
    line.setAttribute('y2', (config.paddingTop + chartHeight).toString());
    line.setAttribute('stroke', '#334155');
    line.setAttribute('stroke-width', '0.5');
    line.setAttribute('stroke-opacity', '0.3');
    gridGroup.appendChild(line);

    // Distance label
    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    text.setAttribute('x', x.toString());
    text.setAttribute('y', (config.paddingTop + chartHeight + 15).toString());
    text.setAttribute('fill', '#94a3b8');
    text.setAttribute('font-size', '10');
    text.setAttribute('text-anchor', 'middle');
    text.textContent = `${d}`;
    gridGroup.appendChild(text);
  }

  // Horizontal grid lines (elevation/depth intervals)
  const zRange = maxZ - minZ;
  const zInterval = Math.max(10, Math.ceil(zRange / 6 / 10) * 10);
  for (let z = Math.floor(minZ / zInterval) * zInterval; z <= maxZ; z += zInterval) {
    const y = yScale(z);
    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    line.setAttribute('x1', config.paddingLeft.toString());
    line.setAttribute('y1', y.toString());
    line.setAttribute('x2', (config.paddingLeft + chartWidth).toString());
    line.setAttribute('y2', y.toString());
    line.setAttribute('stroke', '#334155');
    line.setAttribute('stroke-width', '0.5');
    line.setAttribute('stroke-opacity', '0.3');
    gridGroup.appendChild(line);

    // Elevation/depth label
    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    text.setAttribute('x', (config.paddingLeft - 8).toString());
    text.setAttribute('y', (y + 4).toString());
    text.setAttribute('fill', '#94a3b8');
    text.setAttribute('font-size', '10');
    text.setAttribute('text-anchor', 'end');
    const label = z > 0 ? `+${z}` : z < 0 ? `${z}` : '0';
    text.textContent = label;
    gridGroup.appendChild(text);
  }
}

/**
 * Render reference line (ground level at z=0)
 */
function renderReferenceLine(
  config: RenderConfig,
  yScale: (z: number) => number
): void {
  const refGroup = document.getElementById(`${config.containerId}-reference`);
  if (!refGroup) return;

  refGroup.innerHTML = '';

  const y = yScale(0);
  const chartWidth = config.viewBoxWidth - config.paddingLeft - config.paddingRight;

  const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
  line.setAttribute('x1', config.paddingLeft.toString());
  line.setAttribute('y1', y.toString());
  line.setAttribute('x2', (config.paddingLeft + chartWidth).toString());
  line.setAttribute('y2', y.toString());
  line.setAttribute('class', 'route-reference-ground');
  refGroup.appendChild(line);

  // Label
  const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
  text.setAttribute('x', (config.paddingLeft + 5).toString());
  text.setAttribute('y', (y - 5).toString());
  text.setAttribute('fill', '#64748b');
  text.setAttribute('font-size', '10');
  text.textContent = 'Entry Level';
  refGroup.appendChild(text);
}

/**
 * Render route segments
 */
function renderSegments(
  segments: RouteProfileSegment[],
  points: RouteProfilePoint[],
  config: RenderConfig,
  xScale: (d: number) => number,
  yScale: (z: number) => number
): void {
  const segmentsGroup = document.getElementById(`${config.containerId}-segments`);
  if (!segmentsGroup) return;

  segmentsGroup.innerHTML = '';

  for (const segment of segments) {
    const fromPoint = points.find(p => p.id === segment.fromId);
    const toPoint = points.find(p => p.id === segment.toId);

    if (!fromPoint || !toPoint) continue;

    const x1 = xScale(fromPoint.routeDistanceM);
    const y1 = yScale(fromPoint.zM);
    const x2 = xScale(toPoint.routeDistanceM);
    const y2 = yScale(toPoint.zM);

    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    line.setAttribute('x1', x1.toString());
    line.setAttribute('y1', y1.toString());
    line.setAttribute('x2', x2.toString());
    line.setAttribute('y2', y2.toString());

    const riskClass = segment.traversalRisk === 'high' ? 'route-segment-high-risk' : 
                      segment.traversalRisk === 'moderate' ? 'route-segment-moderate-risk' :
                      'route-segment-mapped';
    line.setAttribute('class', `route-segment ${riskClass}`);
    
    segmentsGroup.appendChild(line);
  }
}

/**
 * Render sector points
 */
function renderSectorPoints(
  points: RouteProfilePoint[],
  config: RenderConfig,
  xScale: (d: number) => number,
  yScale: (z: number) => number
): void {
  const sectorsGroup = document.getElementById(`${config.containerId}-sectors`);
  if (!sectorsGroup) return;

  sectorsGroup.innerHTML = '';

  for (const point of points) {
    const x = xScale(point.routeDistanceM);
    const y = yScale(point.zM);

    const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    circle.setAttribute('cx', x.toString());
    circle.setAttribute('cy', y.toString());
    circle.setAttribute('r', point.type === 'origin' ? '6' : '5');
    circle.setAttribute('class', `route-point route-point-${point.type}`);
    circle.setAttribute('data-tooltip', point.tooltip || point.label);
    circle.setAttribute('data-point-id', point.id);
    
    sectorsGroup.appendChild(circle);

    // Label for origin
    if (point.type === 'origin') {
      const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      text.setAttribute('x', (x + 10).toString());
      text.setAttribute('y', (y + 4).toString());
      text.setAttribute('fill', '#e2e8f0');
      text.setAttribute('font-size', '11');
      text.textContent = point.label;
      sectorsGroup.appendChild(text);
    }
  }
}

/**
 * Render agent points
 */
function renderAgentPoints(
  points: RouteProfilePoint[],
  config: RenderConfig,
  xScale: (d: number) => number,
  yScale: (z: number) => number
): void {
  const agentsGroup = document.getElementById(`${config.containerId}-agents`);
  if (!agentsGroup) return;

  agentsGroup.innerHTML = '';

  for (const point of points) {
    const x = xScale(point.routeDistanceM);
    const y = yScale(point.zM);

    // Determine agent color based on state (matching tactical map styling)
    let agentColor = '#10b981'; // green-500 for active/healthy
    let strokeColor = '#047857'; // green-700 for stroke
    if (point.status === 'degraded' || point.status === 'intermittent') {
      agentColor = '#eab308'; // yellow-500
      strokeColor = '#a16207'; // yellow-700
    } else if (point.status === 'failed' || point.status === 'lost') {
      agentColor = '#ef4444'; // red-500
      strokeColor = '#991b1b'; // red-800
    } else if (point.status === 'landed_relay' || point.status === 'sacrificed') {
      agentColor = '#a855f7'; // purple-500
      strokeColor = '#6d28d9'; // purple-700
    }

    const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    circle.setAttribute('cx', x.toString());
    circle.setAttribute('cy', y.toString());
    circle.setAttribute('r', '6');
    circle.setAttribute('fill', agentColor);
    circle.setAttribute('stroke', strokeColor);
    circle.setAttribute('stroke-width', '1.5');
    circle.setAttribute('class', `route-point route-point-${point.type}`);
    circle.setAttribute('data-tooltip', point.tooltip || point.label);
    circle.setAttribute('data-point-id', point.id);
    
    agentsGroup.appendChild(circle);

    // Label with color matching agent state (like tactical map)
    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    text.setAttribute('x', (x + 10).toString());
    text.setAttribute('y', (y - 8).toString());
    text.setAttribute('fill', agentColor);
    text.setAttribute('font-size', '10');
    text.setAttribute('font-weight', 'bold');
    text.textContent = point.label;
    agentsGroup.appendChild(text);
  }
}

/**
 * Add tooltip interactivity
 */
function addTooltipInteractivity(config: RenderConfig): void {
  const svg = document.getElementById(`${config.containerId}-svg`);
  const tooltip = document.getElementById(`${config.containerId}-tooltip`);
  const tooltipText = document.getElementById(`${config.containerId}-tooltip-text`);

  if (!svg || !tooltip || !tooltipText) return;

  const points = svg.querySelectorAll('.route-point');

  points.forEach(point => {
    point.addEventListener('mouseenter', (e) => {
      const target = e.target as SVGElement;
      const tooltipContent = target.getAttribute('data-tooltip');
      if (tooltipContent) {
        tooltip.style.display = 'block';
        
        // Split tooltip content by newlines
        tooltipText.innerHTML = '';
        const lines = tooltipContent.split('\n');
        lines.forEach((line, index) => {
          const tspan = document.createElementNS('http://www.w3.org/2000/svg', 'tspan');
          tspan.setAttribute('x', '8');
          tspan.setAttribute('dy', index === 0 ? '0' : '14');
          tspan.textContent = line;
          tooltipText.appendChild(tspan);
        });
      }
    });

    point.addEventListener('mousemove', (e) => {
      const mouseEvent = e as MouseEvent;
      const svgRect = svg.getBoundingClientRect();
      const mouseX = mouseEvent.clientX - svgRect.left;
      const mouseY = mouseEvent.clientY - svgRect.top;
      
      // Convert to SVG coordinates
      const svgX = (mouseX / svgRect.width) * config.viewBoxWidth;
      const svgY = (mouseY / svgRect.height) * config.viewBoxHeight;
      
      tooltip.setAttribute('transform', `translate(${svgX + 10}, ${svgY - 30})`);
    });

    point.addEventListener('mouseleave', () => {
      tooltip.style.display = 'none';
    });
  });
}

/**
 * Update route profile with new mission state
 */
export function updateRouteProfile(
  viewModel: RouteProfileViewModel,
  config: Partial<RenderConfig> = {}
): void {
  initializeRouteProfile(viewModel, config);
}
