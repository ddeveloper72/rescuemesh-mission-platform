/**
 * Recommended Actions Manager
 * 
 * Handles interactive recommended actions from mission escalations.
 * Allows operators to acknowledge, execute, or dismiss suggested actions.
 */

export interface RecommendedAction {
  id: string;
  text: string;
  priority: 'critical' | 'high' | 'normal';
  status: 'pending' | 'acknowledged' | 'executing' | 'completed' | 'dismissed';
  category?: 'relay' | 'rescue' | 'exploration' | 'safety' | 'communications';
}

// Track action states
const actionStates = new Map<string, RecommendedAction['status']>();
const actionCallbacks = new Map<string, () => void>();

/**
 * Register an action callback
 */
export function registerActionCallback(actionId: string, callback: () => void) {
  actionCallbacks.set(actionId, callback);
}

/**
 * Execute a recommended action
 */
export function executeAction(actionId: string) {
  // Update state
  actionStates.set(actionId, 'executing');
  
  // Dispatch event for UI update
  window.dispatchEvent(new CustomEvent('action-state-changed', {
    detail: { actionId, status: 'executing' }
  }));
  
  // Execute callback if registered
  const callback = actionCallbacks.get(actionId);
  if (callback) {
    callback();
  }
  
  // Simulate action completion after a delay
  setTimeout(() => {
    actionStates.set(actionId, 'completed');
    window.dispatchEvent(new CustomEvent('action-state-changed', {
      detail: { actionId, status: 'completed' }
    }));
  }, 2000);
  
  console.log(`Executing action: ${actionId}`);
}

/**
 * Acknowledge an action (mark as seen/understood)
 */
export function acknowledgeAction(actionId: string) {
  actionStates.set(actionId, 'acknowledged');
  window.dispatchEvent(new CustomEvent('action-state-changed', {
    detail: { actionId, status: 'acknowledged' }
  }));
  console.log(`Acknowledged action: ${actionId}`);
}

/**
 * Dismiss an action
 */
export function dismissAction(actionId: string) {
  actionStates.set(actionId, 'dismissed');
  window.dispatchEvent(new CustomEvent('action-state-changed', {
    detail: { actionId, status: 'dismissed' }
  }));
  console.log(`Dismissed action: ${actionId}`);
}

/**
 * Get action status
 */
export function getActionStatus(actionId: string): RecommendedAction['status'] {
  return actionStates.get(actionId) || 'pending';
}

/**
 * Reset all action states
 */
export function resetActions() {
  actionStates.clear();
  actionCallbacks.clear();
}

/**
 * Render interactive action buttons in the recommended actions panel
 */
export function renderInteractiveActions(
  escalation: any,
  containerId: string = 'recommended-actions-container'
) {
  const actionsContainer = document.getElementById(containerId);
  if (!actionsContainer || !escalation.active || !escalation.recommended_actions || escalation.recommended_actions.length === 0) {
    if (actionsContainer) {
      actionsContainer.innerHTML = '';
    }
    return;
  }
  
  const actionClasses = {
    'critical': { 
      container: 'bg-red-900/20 border-red-700', 
      header: 'bg-red-900/40 border-red-700', 
      title: 'text-red-200', 
      icon: 'text-red-400', 
      item: 'border-red-700/50',
      itemHover: 'hover:bg-red-900/20',
      button: 'bg-red-700 hover:bg-red-600 text-white'
    },
    'urgent': { 
      container: 'bg-orange-900/20 border-orange-700', 
      header: 'bg-orange-900/40 border-orange-700', 
      title: 'text-orange-200', 
      icon: 'text-orange-400', 
      item: 'border-orange-700/50',
      itemHover: 'hover:bg-orange-900/20',
      button: 'bg-orange-700 hover:bg-orange-600 text-white'
    },
    'warning': { 
      container: 'bg-yellow-900/20 border-yellow-700', 
      header: 'bg-yellow-900/40 border-yellow-700', 
      title: 'text-yellow-200', 
      icon: 'text-yellow-400', 
      item: 'border-yellow-700/50',
      itemHover: 'hover:bg-yellow-900/20',
      button: 'bg-yellow-700 hover:bg-yellow-600 text-white'
    },
    'advisory': { 
      container: 'bg-slate-800/50 border-slate-700', 
      header: 'bg-slate-800 border-slate-700', 
      title: 'text-slate-200', 
      icon: 'text-slate-400', 
      item: 'border-slate-700/50',
      itemHover: 'hover:bg-slate-700/30',
      button: 'bg-slate-600 hover:bg-slate-500 text-white'
    }
  };
  const aClasses = actionClasses[escalation.severity as keyof typeof actionClasses] || actionClasses.advisory;
  
  actionsContainer.innerHTML = `
    <div class="rounded-lg border ${aClasses.container}">
      <div class="px-4 py-3 border-b ${aClasses.header}">
        <h3 class="font-semibold flex items-center gap-2 ${aClasses.title}">
          <svg class="w-5 h-5 ${aClasses.icon}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"/>
          </svg>
          Recommended Actions
        </h3>
      </div>
      <div class="p-4">
        <ul class="space-y-2">
          ${escalation.recommended_actions.map((action: string, index: number) => {
            const actionId = `action-${index}`;
            const isPriority = index === 0 && (escalation.severity === 'critical' || escalation.severity === 'urgent');
            
            return `
              <li class="flex items-start gap-3 p-3 rounded border ${aClasses.item} ${aClasses.itemHover} transition-colors" data-action-id="${actionId}">
                <div class="flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                  escalation.severity === 'critical' || escalation.severity === 'urgent' 
                    ? 'bg-red-700 text-red-100' 
                    : escalation.severity === 'warning'
                    ? 'bg-yellow-700 text-yellow-100'
                    : 'bg-slate-700 text-slate-200'
                }">
                  ${index + 1}
                </div>
                <div class="flex-grow">
                  <div class="text-sm text-slate-200 leading-relaxed pt-0.5 mb-2">
                    ${action}
                  </div>
                  <div class="flex gap-2">
                    <button 
                      class="action-execute-btn px-3 py-1 text-xs font-semibold rounded transition-colors ${aClasses.button}"
                      data-action-id="${actionId}"
                    >
                      Execute
                    </button>
                    <button 
                      class="action-acknowledge-btn px-3 py-1 text-xs font-semibold rounded transition-colors bg-slate-600 hover:bg-slate-500 text-white"
                      data-action-id="${actionId}"
                    >
                      Acknowledge
                    </button>
                    <button 
                      class="action-dismiss-btn px-3 py-1 text-xs font-semibold rounded transition-colors bg-slate-700 hover:bg-slate-600 text-slate-300"
                      data-action-id="${actionId}"
                    >
                      Dismiss
                    </button>
                    <span class="action-status-indicator ml-auto text-xs text-slate-400 pt-1" data-action-id="${actionId}"></span>
                  </div>
                </div>
                ${isPriority 
                  ? '<div class="flex-shrink-0"><span class="text-xs px-2 py-1 rounded bg-red-700 text-red-100 font-semibold">PRIORITY</span></div>'
                  : ''}
              </li>
            `;
          }).join('')}
        </ul>
      </div>
    </div>
  `;
  
  // Attach event listeners to action buttons
  attachActionButtonListeners();
}

/**
 * Attach event listeners to action buttons
 */
function attachActionButtonListeners() {
  // Execute buttons
  document.querySelectorAll('.action-execute-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const target = e.currentTarget as HTMLElement;
      const actionId = target.getAttribute('data-action-id');
      if (actionId) {
        executeAction(actionId);
        updateActionButton(actionId, 'executing');
      }
    });
  });
  
  // Acknowledge buttons
  document.querySelectorAll('.action-acknowledge-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const target = e.currentTarget as HTMLElement;
      const actionId = target.getAttribute('data-action-id');
      if (actionId) {
        acknowledgeAction(actionId);
        updateActionButton(actionId, 'acknowledged');
      }
    });
  });
  
  // Dismiss buttons
  document.querySelectorAll('.action-dismiss-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const target = e.currentTarget as HTMLElement;
      const actionId = target.getAttribute('data-action-id');
      if (actionId) {
        dismissAction(actionId);
        updateActionButton(actionId, 'dismissed');
      }
    });
  });
}

/**
 * Update action button state
 */
function updateActionButton(actionId: string, status: RecommendedAction['status']) {
  const statusIndicator = document.querySelector(`.action-status-indicator[data-action-id="${actionId}"]`);
  if (statusIndicator) {
    const statusLabels = {
      pending: '',
      acknowledged: '✓ Acknowledged',
      executing: '⏳ Executing...',
      completed: '✓ Completed',
      dismissed: 'Dismissed'
    };
    statusIndicator.textContent = statusLabels[status];
    
    const statusColors = {
      pending: 'text-slate-400',
      acknowledged: 'text-blue-400',
      executing: 'text-yellow-400',
      completed: 'text-green-400',
      dismissed: 'text-slate-500'
    };
    statusIndicator.className = `action-status-indicator ml-auto text-xs pt-1 ${statusColors[status]}`;
  }
  
  // Disable buttons after action
  const actionItem = document.querySelector(`li[data-action-id="${actionId}"]`);
  if (actionItem && status !== 'pending') {
    actionItem.querySelectorAll('button').forEach(btn => {
      (btn as HTMLButtonElement).disabled = true;
      btn.classList.add('opacity-50', 'cursor-not-allowed');
    });
  }
}
