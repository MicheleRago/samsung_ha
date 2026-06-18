console.info("%c SAMSUNG OVEN CARD %c v1.0.0 is loaded! ", "color: white; background: #ff9800; font-weight: 700;", "color: #ff9800; background: white; font-weight: 700;");

class SamsungOvenCard extends HTMLElement {
  set hass(hass) {
    if (!this.content) {
      this.card = document.createElement('ha-card');
      this.content = document.createElement('div');
      
      const style = document.createElement('style');
      style.textContent = `
        ha-card {
          border-radius: 24px;
          background: var(--card-background-color);
          color: var(--primary-text-color);
          padding: 24px 16px;
          font-family: var(--paper-font-body1_-_font-family, 'Roboto', sans-serif);
          box-shadow: var(--ha-card-box-shadow, 0px 2px 1px -1px rgba(0, 0, 0, 0.2), 0px 1px 1px 0px rgba(0, 0, 0, 0.14), 0px 1px 3px 0px rgba(0, 0, 0, 0.12));
        }
        .hero {
          display: flex;
          flex-direction: column;
          align-items: center;
          margin-bottom: 24px;
          position: relative;
        }
        .hero ha-icon {
          --mdc-icon-size: 100px;
          color: var(--primary-color, #ff9800);
          margin-bottom: 16px;
          filter: drop-shadow(0px 8px 16px rgba(0,0,0,0.2));
          transition: all 0.3s ease;
        }
        .hero.running ha-icon {
          color: #ff5722;
          animation: pulse-glow 2s infinite;
        }
        .hero-title {
          font-size: 22px;
          font-weight: 600;
        }
        .hero-subtitle {
          font-size: 14px;
          color: var(--secondary-text-color);
          margin-top: 4px;
        }
        .remote-icon {
          position: absolute;
          top: 0;
          right: 16px;
          --mdc-icon-size: 24px;
          color: var(--success-color, #4caf50);
        }
        .remote-icon.disabled {
          color: var(--disabled-text-color, #9e9e9e);
        }
        .grid {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 12px;
        }
        .tile {
          background: var(--secondary-background-color, rgba(120, 120, 120, 0.1));
          border-radius: 16px;
          padding: 16px;
          display: flex;
          flex-direction: column;
          transition: all 0.2s ease;
          position: relative;
        }
        .tile.switch {
          cursor: pointer;
        }
        .tile.switch:active {
          transform: scale(0.96);
        }
        .tile.active {
          background: rgba(var(--rgb-primary-color, 255, 152, 0), 0.15);
        }
        .tile.active .tile-icon {
          color: var(--primary-color, #ff9800);
        }
        .tile-header {
          display: flex;
          align-items: center;
          margin-bottom: 12px;
        }
        .tile-icon {
          width: 36px;
          height: 36px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          background: var(--card-background-color);
          margin-right: 12px;
          color: var(--secondary-text-color);
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .tile-title {
          font-size: 14px;
          font-weight: 500;
        }
        .controls {
          display: flex;
          align-items: center;
          justify-content: space-between;
          background: var(--card-background-color);
          border-radius: 20px;
          padding: 4px;
          box-shadow: inset 0 2px 4px rgba(0,0,0,0.05);
        }
        .controls button {
          background: transparent;
          border: none;
          color: var(--primary-text-color);
          width: 32px;
          height: 32px;
          border-radius: 50%;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: background 0.2s;
        }
        .controls button:hover {
          background: var(--secondary-background-color);
        }
        .controls span {
          font-weight: bold;
          font-size: 16px;
        }
        .select-wrapper {
          margin-top: 12px;
        }
        .select-wrapper select {
          width: 100%;
          padding: 8px 12px;
          border-radius: 8px;
          border: none;
          background: var(--card-background-color);
          color: var(--primary-text-color);
          font-family: inherit;
          font-size: 14px;
          outline: none;
          cursor: pointer;
        }
        .actions {
          display: flex;
          justify-content: center;
          gap: 16px;
          margin-top: 24px;
        }
        .btn-action {
          display: flex;
          flex-direction: column;
          align-items: center;
          background: none;
          border: none;
          cursor: pointer;
          color: var(--primary-text-color);
        }
        .btn-action .icon-wrap {
          width: 56px;
          height: 56px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          background: var(--secondary-background-color);
          margin-bottom: 8px;
          transition: all 0.2s;
        }
        .btn-action:hover .icon-wrap {
          transform: scale(1.05);
        }
        .btn-action:active .icon-wrap {
          transform: scale(0.95);
        }
        .btn-action.start .icon-wrap {
          background: var(--success-color, #4caf50);
          color: white;
          box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
        }
        .btn-action.stop .icon-wrap {
          background: var(--error-color, #f44336);
          color: white;
          box-shadow: 0 4px 12px rgba(244, 67, 54, 0.3);
        }
        .btn-action.pause .icon-wrap {
          background: var(--warning-color, #ff9800);
          color: white;
        }
        @keyframes pulse-glow {
          0% { filter: drop-shadow(0px 0px 8px rgba(255,87,34,0.4)); }
          50% { filter: drop-shadow(0px 0px 16px rgba(255,87,34,0.8)); }
          100% { filter: drop-shadow(0px 0px 8px rgba(255,87,34,0.4)); }
        }
      `;
      
      this.card.appendChild(style);
      this.card.appendChild(this.content);
      this.appendChild(this.card);
      
      // Event bindings
      this.addEventListener('click', e => {
        const action = e.target.closest('[data-action]');
        if (action) {
          const actionType = action.getAttribute('data-action');
          const entity = action.getAttribute('data-entity');
          
          if (actionType === 'toggle' && entity) {
            hass.callService('switch', 'toggle', { entity_id: entity });
          } else if (actionType === 'press' && entity) {
            hass.callService('button', 'press', { entity_id: entity });
          } else if (actionType === 'num_up' || actionType === 'num_down') {
            const state = hass.states[entity];
            if (state) {
              const current = parseFloat(state.state);
              const step = parseFloat(state.attributes.step || 1.0);
              const max = parseFloat(state.attributes.max || 300.0);
              const min = parseFloat(state.attributes.min || 0.0);
              let newVal = actionType === 'num_up' ? current + step : current - step;
              newVal = Math.min(Math.max(newVal, min), max);
              hass.callService('number', 'set_value', { entity_id: entity, value: newVal });
            }
          }
        }
      });
      
      this.addEventListener('change', e => {
        if (e.target.tagName === 'SELECT') {
          const entity = e.target.getAttribute('data-entity');
          hass.callService('select', 'select_option', { entity_id: entity, option: e.target.value });
        }
      });
    }

    const config = this._config;
    
    // Config entities
    const ovenState = hass.states[config.entities.oven_state];
    const currentTemp = hass.states[config.entities.current_temp];
    const targetTemp = hass.states[config.entities.target_temp];
    const cookTime = hass.states[config.entities.cook_time];
    const ovenMode = hass.states[config.entities.oven_mode];
    const light = hass.states[config.entities.light];
    const remote = hass.states[config.entities.remote_control];
    
    const isRunning = ovenState && ['running', 'cooking', 'preheating', 'In Cottura', 'Preriscaldamento'].includes(ovenState.state);
    const isRemoteEnabled = remote && remote.state === 'on';

    let stateText = ovenState ? ovenState.state : 'Unknown';
    if (currentTemp && currentTemp.state !== 'unknown') {
      stateText += ` • ${currentTemp.state}°C`;
    }

    this.content.innerHTML = `
      <div class="hero ${isRunning ? 'running' : ''}">
        <ha-icon class="remote-icon ${!isRemoteEnabled ? 'disabled' : ''}" icon="${isRemoteEnabled ? 'mdi:remote' : 'mdi:remote-off'}" title="Smart Control"></ha-icon>
        <ha-icon icon="${config.icon || 'mdi:stove'}"></ha-icon>
        <div class="hero-title">${config.name || 'Samsung Oven'}</div>
        <div class="hero-subtitle">${stateText}</div>
      </div>
      
      <div class="grid">
        <!-- Target Temp -->
        <div class="tile">
          <div class="tile-header">
            <div class="tile-icon"><ha-icon icon="mdi:thermometer"></ha-icon></div>
            <div class="tile-title">Temp. Target</div>
          </div>
          <div class="controls">
            <button data-action="num_down" data-entity="${config.entities.target_temp}"><ha-icon icon="mdi:minus"></ha-icon></button>
            <span>${targetTemp ? targetTemp.state : '--'} °C</span>
            <button data-action="num_up" data-entity="${config.entities.target_temp}"><ha-icon icon="mdi:plus"></ha-icon></button>
          </div>
        </div>

        <!-- Cook Time -->
        <div class="tile">
          <div class="tile-header">
            <div class="tile-icon"><ha-icon icon="mdi:timer-outline"></ha-icon></div>
            <div class="tile-title">Timer</div>
          </div>
          <div class="controls">
            <button data-action="num_down" data-entity="${config.entities.cook_time}"><ha-icon icon="mdi:minus"></ha-icon></button>
            <span>${cookTime ? cookTime.state : '--'} min</span>
            <button data-action="num_up" data-entity="${config.entities.cook_time}"><ha-icon icon="mdi:plus"></ha-icon></button>
          </div>
        </div>

        <!-- Light -->
        <div class="tile switch ${light && light.state === 'on' ? 'active' : ''}" data-action="toggle" data-entity="${config.entities.light}">
          <div class="tile-header" style="margin: 0;">
            <div class="tile-icon"><ha-icon icon="mdi:lightbulb"></ha-icon></div>
            <div class="tile-title">Luce Forno</div>
          </div>
        </div>
      </div>

      <!-- Mode Select -->
      ${ovenMode ? `
        <div class="tile" style="margin-top: 12px; grid-column: span 2;">
          <div class="tile-header" style="margin-bottom: 0;">
            <div class="tile-icon"><ha-icon icon="mdi:tune-vertical"></ha-icon></div>
            <div class="tile-title">Modalità di Cottura</div>
          </div>
          <div class="select-wrapper">
            <select data-entity="${config.entities.oven_mode}">
              ${ovenMode.attributes.options.map(opt => {
                return `<option value="${opt}" ${opt === ovenMode.state ? 'selected' : ''}>${opt}</option>`;
              }).join('')}
            </select>
          </div>
        </div>
      ` : ''}

      <!-- Action Buttons -->
      <div class="actions">
        ${!isRunning ? `
          <button class="btn-action start" data-action="press" data-entity="${config.entities.start_btn}">
            <div class="icon-wrap"><ha-icon icon="mdi:play"></ha-icon></div>
            <span>Avvia</span>
          </button>
        ` : `
          <button class="btn-action pause" data-action="press" data-entity="${config.entities.pause_btn}">
            <div class="icon-wrap"><ha-icon icon="mdi:pause"></ha-icon></div>
            <span>Pausa</span>
          </button>
          <button class="btn-action stop" data-action="press" data-entity="${config.entities.stop_btn}">
            <div class="icon-wrap"><ha-icon icon="mdi:stop"></ha-icon></div>
            <span>Ferma</span>
          </button>
        `}
      </div>
    `;
  }

  setConfig(config) {
    if (!config.entities) {
      throw new Error("You need to define entities");
    }
    this._config = config;
  }

  getCardSize() {
    return 5;
  }
}

customElements.define('samsung-oven-card', SamsungOvenCard);
window.customCards = window.customCards || [];
window.customCards.push({
  type: "samsung-oven-card",
  name: "Samsung Oven Card",
  preview: true,
  description: "A beautifully animated card for Samsung Smart Ovens"
});
