/**
 * Tactical Map Pan/Zoom Controller
 * 
 * Adds interactive pan and zoom capabilities to SVG tactical maps.
 * Similar to Google Maps: drag to pan, scroll to zoom, reset view button.
 */

interface PanZoomState {
  x: number;
  y: number;
  scale: number;
  minScale: number;
  maxScale: number;
}

interface PanZoomController {
  enable: () => void;
  disable: () => void;
  reset: () => void;
  getState: () => PanZoomState;
  setState: (state: Partial<PanZoomState>) => void;
}

/**
 * Create a pan/zoom controller for an SVG element
 */
export function createPanZoomController(
  svgElement: SVGSVGElement,
  contentGroupId: string = 'map-content',
  options: {
    minScale?: number;
    maxScale?: number;
    zoomSpeed?: number;
  } = {}
): PanZoomController {
  const {
    minScale = 0.5,
    maxScale = 4,
    zoomSpeed = 0.1,
  } = options;

  // Create transformable content group if it doesn't exist
  let contentGroup = svgElement.getElementById(contentGroupId) as SVGGElement;
  if (!contentGroup) {
    contentGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    contentGroup.id = contentGroupId;
    
    // Move all existing children into the new group (except grid pattern and fixed viewport elements)
    const children = Array.from(svgElement.children);
    children.forEach(child => {
      const isGridPattern = child.tagName === 'defs' || 
                           (child.tagName === 'rect' && child.getAttribute('fill') === 'url(#grid)');
      const isFixedElement = child.id === 'map-compass'; // Keep compass outside transform
      
      if (!isGridPattern && !isFixedElement) {
        contentGroup.appendChild(child);
      }
    });
    
    svgElement.appendChild(contentGroup);
  }

  // Pan/zoom state
  const state: PanZoomState = {
    x: 0,
    y: 0,
    scale: 1,
    minScale,
    maxScale,
  };

  // Drag state
  let isDragging = false;
  let dragStartX = 0;
  let dragStartY = 0;
  let dragStartTranslateX = 0;
  let dragStartTranslateY = 0;

  /**
   * Apply current transform to content group
   */
  function applyTransform() {
    contentGroup.setAttribute(
      'transform',
      `translate(${state.x}, ${state.y}) scale(${state.scale})`
    );
  }

  /**
   * Convert client coordinates to SVG coordinates
   */
  function clientToSVGCoordinates(clientX: number, clientY: number): { x: number; y: number } {
    const rect = svgElement.getBoundingClientRect();
    const viewBox = svgElement.viewBox.baseVal;
    
    return {
      x: ((clientX - rect.left) / rect.width) * viewBox.width,
      y: ((clientY - rect.top) / rect.height) * viewBox.height,
    };
  }

  /**
   * Handle mouse wheel zoom
   */
  function handleWheel(event: WheelEvent) {
    event.preventDefault();
    
    const svgCoords = clientToSVGCoordinates(event.clientX, event.clientY);
    
    // Calculate zoom
    const delta = -event.deltaY;
    const zoomFactor = delta > 0 ? (1 + zoomSpeed) : (1 - zoomSpeed);
    const newScale = Math.min(state.maxScale, Math.max(state.minScale, state.scale * zoomFactor));
    
    if (newScale !== state.scale) {
      // Zoom toward cursor position
      const scaleDiff = newScale - state.scale;
      state.x -= (svgCoords.x - state.x) * (scaleDiff / state.scale);
      state.y -= (svgCoords.y - state.y) * (scaleDiff / state.scale);
      state.scale = newScale;
      
      applyTransform();
    }
  }

  /**
   * Handle mouse down - start drag
   */
  function handleMouseDown(event: MouseEvent) {
    if (event.button !== 0) return; // Only left click
    
    isDragging = true;
    dragStartX = event.clientX;
    dragStartY = event.clientY;
    dragStartTranslateX = state.x;
    dragStartTranslateY = state.y;
    
    svgElement.style.cursor = 'grabbing';
    
    // Attach move/up handlers to document for better drag behavior
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
    
    event.preventDefault();
  }

  /**
   * Handle mouse move - drag
   */
  function handleMouseMove(event: MouseEvent) {
    if (!isDragging) return;
    
    const rect = svgElement.getBoundingClientRect();
    const viewBox = svgElement.viewBox.baseVal;
    
    const dx = ((event.clientX - dragStartX) / rect.width) * viewBox.width;
    const dy = ((event.clientY - dragStartY) / rect.height) * viewBox.height;
    
    state.x = dragStartTranslateX + dx;
    state.y = dragStartTranslateY + dy;
    
    applyTransform();
    event.preventDefault();
  }

  /**
   * Handle mouse up - end drag
   */
  function handleMouseUp() {
    if (isDragging) {
      isDragging = false;
      svgElement.style.cursor = 'grab';
      
      // Remove document-level handlers
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    }
  }

  /**
   * Handle touch start - start drag
   */
  function handleTouchStart(event: TouchEvent) {
    if (event.touches.length === 1) {
      const touch = event.touches[0];
      isDragging = true;
      dragStartX = touch.clientX;
      dragStartY = touch.clientY;
      dragStartTranslateX = state.x;
      dragStartTranslateY = state.y;
      event.preventDefault();
    }
  }

  /**
   * Handle touch move - drag
   */
  function handleTouchMove(event: TouchEvent) {
    if (!isDragging || event.touches.length !== 1) return;
    
    const touch = event.touches[0];
    const rect = svgElement.getBoundingClientRect();
    const viewBox = svgElement.viewBox.baseVal;
    
    const dx = ((touch.clientX - dragStartX) / rect.width) * viewBox.width;
    const dy = ((touch.clientY - dragStartY) / rect.height) * viewBox.height;
    
    state.x = dragStartTranslateX + dx;
    state.y = dragStartTranslateY + dy;
    
    applyTransform();
    event.preventDefault();
  }

  /**
   * Handle touch end - end drag
   */
  function handleTouchEnd() {
    isDragging = false;
  }

  /**
   * Enable pan/zoom controls
   */
  function enable() {
    svgElement.style.cursor = 'grab';
    
    svgElement.addEventListener('wheel', handleWheel, { passive: false });
    svgElement.addEventListener('mousedown', handleMouseDown);
    svgElement.addEventListener('mouseleave', handleMouseUp);
    
    svgElement.addEventListener('touchstart', handleTouchStart, { passive: false });
    svgElement.addEventListener('touchmove', handleTouchMove, { passive: false });
    svgElement.addEventListener('touchend', handleTouchEnd);
    svgElement.addEventListener('touchcancel', handleTouchEnd);
    
    applyTransform();
  }

  /**
   * Disable pan/zoom controls
   */
  function disable() {
    svgElement.style.cursor = '';
    
    // Clean up any active drag
    if (isDragging) {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      isDragging = false;
    }
    
    svgElement.removeEventListener('wheel', handleWheel);
    svgElement.removeEventListener('mousedown', handleMouseDown);
    svgElement.removeEventListener('mouseleave', handleMouseUp);
    
    svgElement.removeEventListener('touchstart', handleTouchStart);
    svgElement.removeEventListener('touchmove', handleTouchMove);
    svgElement.removeEventListener('touchend', handleTouchEnd);
    svgElement.removeEventListener('touchcancel', handleTouchEnd);
  }

  /**
   * Reset to default view
   */
  function reset() {
    state.x = 0;
    state.y = 0;
    state.scale = 1;
    applyTransform();
  }

  /**
   * Get current state
   */
  function getState(): PanZoomState {
    return { ...state };
  }

  /**
   * Set state
   */
  function setState(newState: Partial<PanZoomState>) {
    if (newState.x !== undefined) state.x = newState.x;
    if (newState.y !== undefined) state.y = newState.y;
    if (newState.scale !== undefined) {
      state.scale = Math.min(state.maxScale, Math.max(state.minScale, newState.scale));
    }
    applyTransform();
  }

  return {
    enable,
    disable,
    reset,
    getState,
    setState,
  };
}
