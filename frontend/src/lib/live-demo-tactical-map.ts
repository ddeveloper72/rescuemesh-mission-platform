import { createPanZoomController } from './tactical-map-pan-zoom';

export function initializeTacticalMapPanZoom(): ReturnType<typeof createPanZoomController> | null {
  const svgElement = document.getElementById('tactical-map-svg') as SVGSVGElement | null;
  if (!svgElement) {
    return null;
  }

  const panZoomController = createPanZoomController(svgElement, 'map-content', {
    minScale: 0.5,
    maxScale: 5,
    zoomSpeed: 0.15,
  });
  panZoomController.enable();

  document.getElementById('map-zoom-in')?.addEventListener('click', () => {
    const state = panZoomController.getState();
    panZoomController.setState({ scale: state.scale * 1.3 });
  });

  document.getElementById('map-zoom-out')?.addEventListener('click', () => {
    const state = panZoomController.getState();
    panZoomController.setState({ scale: state.scale / 1.3 });
  });

  document.getElementById('map-reset-view')?.addEventListener('click', () => {
    panZoomController.reset();
  });

  return panZoomController;
}
