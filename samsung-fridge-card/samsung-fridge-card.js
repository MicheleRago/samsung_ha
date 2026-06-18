class SamsungFridgeCard extends HTMLElement {
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
        }
        .hero img {
          width: 140px;
          height: auto;
          margin-bottom: 16px;
          filter: drop-shadow(0px 8px 16px rgba(0,0,0,0.3));
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
          overflow: hidden;
        }
        .tile.switch {
          cursor: pointer;
        }
        .tile.switch:active {
          transform: scale(0.96);
        }
        .tile.active {
          background: rgba(var(--rgb-primary-color, 3, 169, 244), 0.15);
        }
        .tile.active .tile-icon {
          color: var(--primary-color, #03a9f4);
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
        .sensors {
          display: flex;
          justify-content: space-around;
          margin-top: 24px;
          padding-top: 16px;
          border-top: 1px solid var(--divider-color, rgba(120, 120, 120, 0.2));
        }
        .sensor {
          display: flex;
          flex-direction: column;
          align-items: center;
        }
        .sensor-icon {
          color: var(--secondary-text-color);
          margin-bottom: 6px;
        }
        .sensor.alert .sensor-icon {
          color: var(--error-color, #f44336);
          animation: pulse 2s infinite;
        }
        .sensor-val {
          font-size: 12px;
          font-weight: 500;
        }
        @keyframes pulse {
          0% { opacity: 1; }
          50% { opacity: 0.5; }
          100% { opacity: 1; }
        }
      `;
      
      this.card.appendChild(style);
      this.card.appendChild(this.content);
      this.appendChild(this.card);
      
      // Events bound once
      this.addEventListener('click', e => {
        const action = e.target.closest('[data-action]');
        if (action) {
          const actionType = action.getAttribute('data-action');
          const entity = action.getAttribute('data-entity');
          
          if (actionType === 'toggle') {
            hass.callService('switch', 'toggle', { entity_id: entity });
          } else if (actionType === 'temp_up' || actionType === 'temp_down') {
            const state = hass.states[entity];
            if (state) {
              const current = parseFloat(state.state);
              const step = parseFloat(state.attributes.step || 1.0);
              const max = parseFloat(state.attributes.max || 10.0);
              const min = parseFloat(state.attributes.min || -25.0);
              let newVal = actionType === 'temp_up' ? current + step : current - step;
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
    const tempFridge = hass.states[config.entities.temp_fridge];
    const tempFreezer = hass.states[config.entities.temp_freezer];
    const coolSwitch = hass.states[config.entities.power_cool];
    const freezeSwitch = hass.states[config.entities.power_freeze];
    const modeSelect = hass.states[config.entities.freezer_mode];
    const doorFridge = hass.states[config.entities.door_fridge];
    const doorFreezer = hass.states[config.entities.door_freezer];

    const image = config.image || 'https://images.samsung.com/is/image/samsung/p6pim/it/rb38a7b6bs9-ef/gallery/it-bespoke-refrigerator-rb38a7b6bs9-ef-531086053?$650_519_PNG$'; // Fallback image

    this.content.innerHTML = `
      <div class="hero">
        <img src="${image}" alt="Refrigerator" />
        <div class="hero-title">${config.name || 'Samsung Refrigerator'}</div>
        <div class="hero-subtitle">Online</div>
      </div>
      
      <div class="grid">
        <!-- Temp Frigo -->
        <div class="tile">
          <div class="tile-header">
            <div class="tile-icon"><ha-icon icon="mdi:fridge-top"></ha-icon></div>
            <div class="tile-title">Temp. Frigo</div>
          </div>
          <div class="controls">
            <button data-action="temp_down" data-entity="${config.entities.temp_fridge}"><ha-icon icon="mdi:minus"></ha-icon></button>
            <span>${tempFridge ? tempFridge.state : '--'} °C</span>
            <button data-action="temp_up" data-entity="${config.entities.temp_fridge}"><ha-icon icon="mdi:plus"></ha-icon></button>
          </div>
        </div>

        <!-- Temp Freezer -->
        <div class="tile">
          <div class="tile-header">
            <div class="tile-icon"><ha-icon icon="mdi:fridge-bottom"></ha-icon></div>
            <div class="tile-title">Temp. Freezer</div>
          </div>
          <div class="controls">
            <button data-action="temp_down" data-entity="${config.entities.temp_freezer}"><ha-icon icon="mdi:minus"></ha-icon></button>
            <span>${tempFreezer ? tempFreezer.state : '--'} °C</span>
            <button data-action="temp_up" data-entity="${config.entities.temp_freezer}"><ha-icon icon="mdi:plus"></ha-icon></button>
          </div>
        </div>

        <!-- Power Cool -->
        <div class="tile switch ${coolSwitch && coolSwitch.state === 'on' ? 'active' : ''}" data-action="toggle" data-entity="${config.entities.power_cool}">
          <div class="tile-header" style="margin: 0;">
            <div class="tile-icon"><ha-icon icon="mdi:snowflake-alert"></ha-icon></div>
            <div class="tile-title">Power Cool</div>
          </div>
        </div>

        <!-- Power Freeze -->
        <div class="tile switch ${freezeSwitch && freezeSwitch.state === 'on' ? 'active' : ''}" data-action="toggle" data-entity="${config.entities.power_freeze}">
          <div class="tile-header" style="margin: 0;">
            <div class="tile-icon"><ha-icon icon="mdi:snowflake-melt"></ha-icon></div>
            <div class="tile-title">Power Freeze</div>
          </div>
        </div>
      </div>

      <!-- Freezer Mode Select -->
      ${modeSelect ? `
        <div class="tile" style="margin-top: 12px; grid-column: span 2;">
          <div class="tile-header" style="margin-bottom: 0;">
            <div class="tile-icon"><ha-icon icon="mdi:tune-vertical"></ha-icon></div>
            <div class="tile-title">Modalità Freezer</div>
          </div>
          <div class="select-wrapper">
            <select data-entity="${config.entities.freezer_mode}">
              ${modeSelect.attributes.options.map(opt => `
                <option value="${opt}" ${opt === modeSelect.state ? 'selected' : ''}>${opt}</option>
              `).join('')}
            </select>
          </div>
        </div>
      ` : ''}

      <!-- Sensors -->
      <div class="sensors">
        <div class="sensor ${doorFridge && doorFridge.state === 'on' ? 'alert' : ''}">
          <ha-icon class="sensor-icon" icon="${doorFridge && doorFridge.state === 'on' ? 'mdi:door-open' : 'mdi:door-closed'}"></ha-icon>
          <div class="sensor-val">${doorFridge && doorFridge.state === 'on' ? 'Aperta' : 'Chiusa'}</div>
        </div>
        <div class="sensor ${doorFreezer && doorFreezer.state === 'on' ? 'alert' : ''}">
          <ha-icon class="sensor-icon" icon="${doorFreezer && doorFreezer.state === 'on' ? 'mdi:door-open' : 'mdi:door-closed'}"></ha-icon>
          <div class="sensor-val">${doorFreezer && doorFreezer.state === 'on' ? 'Aperta' : 'Chiusa'}</div>
        </div>
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
    return 4;
  }
}

customElements.define('samsung-fridge-card', SamsungFridgeCard);
window.customCards = window.customCards || [];
window.customCards.push({
  type: "samsung-fridge-card",
  name: "Samsung Fridge Card",
  preview: true,
  description: "A beautifully animated card for Samsung Refrigerators"
});
