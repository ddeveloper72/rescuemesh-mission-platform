/**
 * Tactical Map Pan/Zoom Controller
 * 
 * Provides interactive pan (drag) and zoom capabilities for SVG tactical maps,
 * similar to modern web mapping interfaces (Google Maps, Leaflet, etc.).
 * 
 * **Key Features:**
 * - Mouse drag to pan the map view
 * - Mouse wheel to zoom in/out at cursor position
 * - Programmatic zoom controls (zoom in/out buttons)
 * - Reset view to default state
 * - Configurable zoom limits (minScale, maxScale)
 * - Smooth transform updates via SVG transforms
 * 
 * **Critical Implementation Detail: Document-Level Event Handlers**
 * 
 * The drag functionality uses document-level event listeners for mousemove and mouseup,
 * rather than element-level listeners. This pattern is essential because:
 * 
 * 1. **DOM Update Resilience:** When the SVG content is dynamically updated (e.g., mission
 *    state polling every 2 seconds), element-level listeners can be detached and lost.
 *    Document-level listeners persist across DOM updates.
 * 
 * 2. **Cursor Tracking:** Document-level listeners continue tracking the mouse even when
 *    the cursor moves outside the SVG boundaries during a drag operation.
 * 
 * 3. **Clean State Management:** Handlers are attached on mousedown and removed on mouseup,
 *    ensuring no memory leaks or duplicate handlers.
 * 
 * This pattern enables smooth panning even during live mission updates.
 * 
 * @module tactical-map-pan-zoom
 */

interface PanZoomState {
  x: number;        // X translation in viewBox units
  y: number;        // Y translation in viewBox units
  scale: number;    // Zoom scale factor (1.0 = 100%)
  minScale: number; // Minimum allowed zoom (e.g., 0.5 = 50%)
  maxScale: number; // Maximum allowed zoom (e.g., 4.0 = 400%)
}

interface PanZoomController {
  enable: () => void;                              // Attach event listeners
  disable: () => void;                             // Detach event listeners
  reset: () => void;                               // Reset to default view
  getState: () => PanZoomState;                    // Get current transform state
  setState: (state: Partial<PanZoomState>) => void; // Programmatically set state
}

/**
 * Create a pan/zoom controller for an SVG tactical map element.
 * 
 * @param svgElement - The root SVG element to control
 * @param contentGroupId - ID of the SVG group element to transform (default: 'map-content')
 * @param options - Configuration options for zoom limits and speed
 * @returns Controller object with enable/disable/reset methods
 * 
 * @example
 * ```typescript
 * const svg = document.getElementById('tactical-map-svg') as SVGSVGElement;
 * const controller = createPanZoomController(svg, 'map-content', {
 *   minScale: 0.5,
 *   maxScale: 5.0,
 *   zoomSpeed: 0.15
 * });
 * controller.enable();
 * ```
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
   * Handle mouse down event - initiate drag operation.
   * 
   * This handler:
   * 1. Records the starting cursor position and current transform state
   * 2. Attaches mousemove/mouseup handlers to the DOCUMENT (not the SVG element)
   * 3. Changes cursor to 'grabbing' for visual feedback
   * 
   * **Why document-level handlers?**
   * - Survives DOM updates during live mission state polling
   * - Tracks cursor even when it leaves the SVG boundaries
   * - Clean attachment/detachment on mouse down/up cycle
   * 
   * @param event - Mouse down event (only responds to left click)
   */
  function handleMouseDown(event: MouseEvent) {
    if (event.button !== 0) return; // Only left click
    
    isDragging = true;
    dragStartX = event.clientX;
    dragStartY = event.clientY;
    dragStartTranslateX = state.x;
    dragStartTranslateY = state.y;
    
    svgElement.style.cursor = 'grabbing';
    
    // CRITICAL: Attach handlers to document, not SVG element
    // This ensures they persist across DOM updates and track cursor outside SVG
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
    
    event.preventDefault();
  }

  /**
   * Handle mouse move event - update map position during drag.
   * 
   * Calculates the delta from drag start position and applies it to the
   * transform, accounting for viewBox coordinate system and current zoom level.
   * 
   * @param event - Mouse move event
   */
  function handleMouseMove(event: MouseEvent) {
    if (!isDragging) return;
    
    const rect = svgElement.getBoundingClientRect();
    const viewBox = svgElement.viewBox.baseVal;
    
    // Convert screen-space pixel delta to viewBox coordinate delta
    const dx = ((event.clientX - dragStartX) / rect.width) * viewBox.width;
    const dy = ((event.clientY - dragStartY) / rect.height) * viewBox.height;
    
    state.x = dragStartTranslateX + dx;
    state.y = dragStartTranslateY + dy;
    
    applyTransform();
    event.preventDefault();
  }

  /**
   * Handle mouse up event - end drag operation.
   * 
   * Cleans up the drag state by:
   * 1. Resetting the isDragging flag
   * 2. Restoring cursor to 'grab' (hover state)
   * 3. Removing document-level event handlers to prevent memory leaks
   * 
   * This ensures clean state management and no orphaned event listeners.
   * 
   * @param event - Mouse up event
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
