console.info("%c SAMSUNG DISHWASHER CARD %c v1.0.0 is loaded! ", "color: white; background: #00a6a6; font-weight: 700;", "color: #00a6a6; background: white; font-weight: 700;");

class SamsungDishwasherCard extends HTMLElement {
  set hass(hass) {
    this._hass = hass;

    if (!this.content) {
      this.card = document.createElement('ha-card');
      this.content = document.createElement('div');

      const style = document.createElement('style');
      style.textContent = `
        ha-card {
          border-radius: 8px;
          background: var(--card-background-color);
          color: var(--primary-text-color);
          padding: 18px;
          font-family: var(--paper-font-body1_-_font-family, 'Roboto', sans-serif);
          box-shadow: var(--ha-card-box-shadow, 0 2px 1px -1px rgba(0, 0, 0, 0.2), 0 1px 1px 0 rgba(0, 0, 0, 0.14), 0 1px 3px 0 rgba(0, 0, 0, 0.12));
        }
        .hero {
          display: grid;
          grid-template-columns: 64px 1fr auto;
          gap: 14px;
          align-items: center;
          margin-bottom: 16px;
        }
        .hero-icon {
          width: 64px;
          height: 64px;
          border-radius: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: rgba(0, 166, 166, 0.14);
          color: #00a6a6;
        }
        .hero-icon ha-icon {
          --mdc-icon-size: 42px;
        }
        .hero.running .hero-icon {
          color: #1976d2;
          background: rgba(25, 118, 210, 0.16);
        }
        .hero.paused .hero-icon {
          color: #f57c00;
          background: rgba(245, 124, 0, 0.16);
        }
        .hero-title {
          font-size: 20px;
          line-height: 1.2;
          font-weight: 600;
          overflow-wrap: anywhere;
        }
        .hero-subtitle {
          margin-top: 4px;
          font-size: 13px;
          color: var(--secondary-text-color);
          overflow-wrap: anywhere;
        }
        .remote {
          display: flex;
          align-items: center;
          justify-content: center;
          width: 34px;
          height: 34px;
          border-radius: 8px;
          color: var(--disabled-text-color, #9e9e9e);
          background: var(--secondary-background-color, rgba(120, 120, 120, 0.12));
        }
        .remote.enabled {
          color: #2e7d32;
          background: rgba(46, 125, 50, 0.14);
        }
        .remote ha-icon {
          --mdc-icon-size: 20px;
        }
        .status-line {
          height: 4px;
          border-radius: 999px;
          background: var(--divider-color, rgba(120, 120, 120, 0.24));
          overflow: hidden;
          margin-bottom: 16px;
        }
        .status-line span {
          display: block;
          width: 100%;
          height: 100%;
          background: #00a6a6;
        }
        .status-line.running span {
          background: linear-gradient(90deg, #00a6a6, #1976d2);
          animation: wash-flow 1.6s linear infinite;
          background-size: 200% 100%;
        }
        .status-line.paused span {
          background: #f57c00;
        }
        .metrics {
          display: grid;
          grid-template-columns: repeat(2, minmax(0, 1fr));
          gap: 10px;
        }
        .tile {
          min-width: 0;
          border-radius: 8px;
          padding: 12px;
          background: var(--secondary-background-color, rgba(120, 120, 120, 0.1));
        }
        .tile.full {
          grid-column: 1 / -1;
        }
        .tile-header {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 8px;
          color: var(--secondary-text-color);
          font-size: 12px;
          font-weight: 500;
          text-transform: uppercase;
        }
        .tile-header ha-icon {
          --mdc-icon-size: 18px;
        }
        .tile-value {
          min-height: 22px;
          font-size: 16px;
          font-weight: 600;
          line-height: 1.25;
          overflow-wrap: anywhere;
        }
        .select-wrapper select {
          width: 100%;
          min-height: 38px;
          border-radius: 8px;
          border: 1px solid var(--divider-color, rgba(120, 120, 120, 0.24));
          background: var(--card-background-color);
          color: var(--primary-text-color);
          font: inherit;
          outline: none;
          padding: 7px 10px;
        }
        .option-grid {
          display: grid;
          grid-template-columns: repeat(2, minmax(0, 1fr));
          gap: 10px;
          margin-top: 10px;
        }
        .switch-tile {
          display: flex;
          align-items: center;
          gap: 10px;
          min-height: 52px;
          border: 0;
          border-radius: 8px;
          padding: 10px 12px;
          color: var(--primary-text-color);
          background: var(--secondary-background-color, rgba(120, 120, 120, 0.1));
          font: inherit;
          text-align: left;
          cursor: pointer;
        }
        .switch-tile:active {
          transform: scale(0.98);
        }
        .switch-tile.active {
          background: rgba(0, 166, 166, 0.16);
        }
        .switch-tile ha-icon {
          --mdc-icon-size: 22px;
          color: var(--secondary-text-color);
          flex: 0 0 auto;
        }
        .switch-tile.active ha-icon {
          color: #00a6a6;
        }
        .switch-title {
          font-size: 14px;
          font-weight: 600;
          line-height: 1.2;
          overflow-wrap: anywhere;
        }
        .switch-state {
          display: block;
          margin-top: 2px;
          font-size: 12px;
          color: var(--secondary-text-color);
        }
        .actions {
          display: flex;
          justify-content: center;
          gap: 12px;
          margin-top: 16px;
          flex-wrap: wrap;
        }
        .action-btn {
          min-width: 82px;
          border: 0;
          border-radius: 8px;
          padding: 10px 12px;
          color: var(--primary-text-color);
          background: var(--secondary-background-color, rgba(120, 120, 120, 0.12));
          font: inherit;
          font-weight: 600;
          cursor: pointer;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
        }
        .action-btn ha-icon {
          --mdc-icon-size: 20px;
        }
        .action-btn.start {
          background: #2e7d32;
          color: white;
        }
        .action-btn.pause {
          background: #f57c00;
          color: white;
        }
        .action-btn.stop {
          background: #c62828;
          color: white;
        }
        .warnings {
          display: grid;
          gap: 8px;
          margin-top: 12px;
        }
        .warning {
          display: flex;
          align-items: center;
          gap: 8px;
          border-radius: 8px;
          padding: 9px 10px;
          color: #8a4b00;
          background: rgba(245, 124, 0, 0.14);
          font-size: 13px;
          font-weight: 500;
        }
        .warning ha-icon {
          --mdc-icon-size: 18px;
        }
        @keyframes wash-flow {
          0% { background-position: 0 0; }
          100% { background-position: 200% 0; }
        }
        @media (max-width: 420px) {
          ha-card {
            padding: 14px;
          }
          .hero {
            grid-template-columns: 52px 1fr auto;
            gap: 10px;
          }
          .hero-icon {
            width: 52px;
            height: 52px;
          }
          .hero-icon ha-icon {
            --mdc-icon-size: 34px;
          }
          .metrics,
          .option-grid {
            grid-template-columns: 1fr;
          }
          .action-btn {
            flex: 1 1 92px;
          }
        }
      `;

      this.card.appendChild(style);
      this.card.appendChild(this.content);
      this.appendChild(this.card);

      this.addEventListener('click', event => {
        const action = event.target.closest('[data-action]');
        if (!action || !this._hass) {
          return;
        }
        const actionType = action.getAttribute('data-action');
        const entity = action.getAttribute('data-entity');
        if (!entity) {
          return;
        }

        if (actionType === 'toggle') {
          const domain = entity.split('.')[0];
          this._hass.callService(domain, 'toggle', { entity_id: entity });
        } else if (actionType === 'press') {
          this._hass.callService('button', 'press', { entity_id: entity });
        }
      });

      this.addEventListener('change', event => {
        if (!this._hass || event.target.tagName !== 'SELECT') {
          return;
        }
        const entity = event.target.getAttribute('data-entity');
        if (entity) {
          this._hass.callService('select', 'select_option', {
            entity_id: entity,
            option: event.target.value,
          });
        }
      });
    }

    const config = this._config;
    const entities = config.entities || {};
    const getState = key => entities[key] ? hass.states[entities[key]] : undefined;
    const entityId = key => entities[key] || '';

    const machine = getState('machine_state');
    const job = getState('job_state');
    const remaining = getState('remaining_time');
    const completion = getState('completion_time');
    const course = getState('course');
    const remote = getState('remote_control');
    const door = getState('door');
    const power = getState('power');

    const machineState = this._state(machine);
    const jobState = this._state(job);
    const remainingValue = this._state(remaining);
    const completionValue = this._state(completion);
    const remoteEnabled = this._isTruthy(this._state(remote));
    const doorOpen = this._isDoorOpen(this._state(door));
    const powerOff = power && this._state(power) === 'off';
    const isPaused = this._isPaused(machineState);
    const isRunning = this._isRunning(machineState, jobState);
    const statusClass = isPaused ? 'paused' : isRunning ? 'running' : 'ready';

    const subtitleParts = [
      this._stateLabel(machineState),
      jobState ? this._jobLabel(jobState) : '',
      remainingValue ? this._formatDuration(remainingValue) : '',
    ].filter(Boolean);

    const metricTiles = [
      this._renderMetric('Stato', this._stateLabel(machineState), 'mdi:dishwasher'),
      this._renderMetric('Fase', this._jobLabel(jobState), 'mdi:state-machine'),
      this._renderMetric('Residuo', this._formatDuration(remainingValue), 'mdi:timer-outline'),
      this._renderMetric('Fine', this._formatDateTime(completionValue), 'mdi:clock-outline'),
    ].filter(Boolean).join('');

    const courseHtml = course && Array.isArray(course.attributes.options) ? `
      <div class="tile full">
        <div class="tile-header"><ha-icon icon="mdi:tune-vertical"></ha-icon><span>Programma</span></div>
        <div class="select-wrapper">
          <select data-entity="${this._escapeAttr(entityId('course'))}">
            ${course.attributes.options.map(option => {
              const selected = option === course.state || this._courseLabel(option) === this._courseLabel(course.state);
              return `<option value="${this._escapeAttr(option)}" ${selected ? 'selected' : ''}>${this._escapeHtml(this._courseLabel(option))}</option>`;
            }).join('')}
          </select>
        </div>
      </div>
    ` : '';

    const optionTiles = [
      this._renderSwitch(getState('half_load'), entityId('half_load'), 'Mezzo carico', 'mdi:circle-half-full'),
      this._renderSwitch(getState('speed_booster'), entityId('speed_booster'), 'Speed Booster', 'mdi:fast-forward'),
      this._renderSwitch(getState('sanitize'), entityId('sanitize'), 'Sanitizzazione', 'mdi:water-boiler'),
      this._renderSwitch(getState('auto_open_door'), entityId('auto_open_door'), 'Auto apertura', 'mdi:door-open'),
      this._renderSwitch(power, entityId('power'), 'Power', 'mdi:power'),
    ].filter(Boolean).join('');

    const runEntity = entityId('run_btn') || entityId('start_btn');
    const pauseEntity = entityId('pause_btn');
    const stopEntity = entityId('stop_btn');
    const actions = this._renderActions(runEntity, pauseEntity, stopEntity, isRunning, isPaused);

    const warnings = [
      remote && !remoteEnabled ? this._renderWarning('mdi:remote-off', 'Smart Control non attivo') : '',
      doorOpen ? this._renderWarning('mdi:door-open', 'Porta aperta') : '',
      powerOff ? this._renderWarning('mdi:power', 'Lavastoviglie spenta') : '',
    ].filter(Boolean).join('');

    this.content.innerHTML = `
      <div class="hero ${statusClass}">
        <div class="hero-icon"><ha-icon icon="${this._escapeAttr(config.icon || 'mdi:dishwasher')}"></ha-icon></div>
        <div>
          <div class="hero-title">${this._escapeHtml(config.name || 'Lavastoviglie Samsung')}</div>
          <div class="hero-subtitle">${this._escapeHtml(subtitleParts.join(' - ') || 'Stato non disponibile')}</div>
        </div>
        ${remote ? `<div class="remote ${remoteEnabled ? 'enabled' : ''}"><ha-icon icon="${remoteEnabled ? 'mdi:remote' : 'mdi:remote-off'}"></ha-icon></div>` : ''}
      </div>

      <div class="status-line ${statusClass}"><span></span></div>

      <div class="metrics">
        ${metricTiles}
        ${courseHtml}
      </div>

      ${optionTiles ? `<div class="option-grid">${optionTiles}</div>` : ''}
      ${actions}
      ${warnings ? `<div class="warnings">${warnings}</div>` : ''}
    `;
  }

  setConfig(config) {
    if (!config.entities) {
      throw new Error('You need to define entities');
    }
    this._config = config;
  }

  getCardSize() {
    return 5;
  }

  _state(entity) {
    if (!entity || entity.state === 'unknown' || entity.state === 'unavailable') {
      return '';
    }
    return entity.state;
  }

  _isTruthy(value) {
    return ['on', 'true', 'enabled', 'yes'].includes(String(value).toLowerCase());
  }

  _isDoorOpen(value) {
    return ['on', 'open', 'opened', 'true'].includes(String(value).toLowerCase());
  }

  _isPaused(value) {
    return ['pause', 'paused', 'in pausa'].includes(String(value).toLowerCase());
  }

  _isRunning(machineState, jobState) {
    const machine = String(machineState).toLowerCase();
    const job = String(jobState).toLowerCase();
    if (['run', 'running'].includes(machine)) {
      return true;
    }
    if (this._isPaused(machine)) {
      return true;
    }
    return !!job && !['ready', 'finish', 'finished', 'finito', 'none', 'idle', 'stop', 'stopped'].includes(job);
  }

  _stateLabel(value) {
    const labels = {
      ready: 'Pronta',
      run: 'In corso',
      running: 'In corso',
      pause: 'In pausa',
      paused: 'In pausa',
      stop: 'Ferma',
      stopped: 'Ferma',
      off: 'Spenta',
      on: 'Accesa',
    };
    return labels[String(value).toLowerCase()] || value || '--';
  }

  _jobLabel(value) {
    const labels = {
      air_wash: 'Lavaggio ad aria',
      cooling: 'Raffreddamento',
      drying: 'Asciugatura',
      dry: 'Asciugatura',
      finish: 'Finito',
      finished: 'Finito',
      pre_wash: 'Prelavaggio',
      prewash: 'Prelavaggio',
      ready: 'Pronta',
      rinse: 'Risciacquo',
      rinsing: 'Risciacquo',
      spin: 'Centrifuga',
      wash: 'Lavaggio',
      washing: 'Lavaggio',
      wrinkle_prevent: 'Antipiega',
    };
    return labels[String(value).toLowerCase()] || value || '--';
  }

  _courseLabel(value) {
    if (!value) {
      return '--';
    }
    let course = String(value);
    if (course.includes('_Course_')) {
      course = course.split('_Course_').pop();
    }
    const labels = {
      auto: 'Auto',
      daily: 'Giornaliero',
      normal: 'Normale',
      eco: 'Eco',
      intensive: 'Intensivo',
      delicate: 'Delicati',
      quick: 'Rapido',
      express: 'Express',
      express60: 'Express 60',
      rinse: 'Risciacquo',
      prewash: 'Prelavaggio',
      pre_wash: 'Prelavaggio',
      selfclean: 'Pulizia vasca',
      self_clean: 'Pulizia vasca',
      machinecare: 'Cura macchina',
      machine_care: 'Cura macchina',
    };
    return labels[course.toLowerCase()] || course.replace(/_/g, ' ');
  }

  _formatDuration(value) {
    if (!value) {
      return '--';
    }
    const text = String(value);
    const match = text.match(/^(\d{1,2}):(\d{2})(?::(\d{2}))?$/);
    if (!match) {
      return text;
    }
    const hours = parseInt(match[1], 10);
    const minutes = parseInt(match[2], 10);
    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
  }

  _formatDateTime(value) {
    if (!value) {
      return '--';
    }
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) {
      return value;
    }
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  _renderMetric(title, value, icon) {
    if (!value || value === '--') {
      return '';
    }
    return `
      <div class="tile">
        <div class="tile-header"><ha-icon icon="${this._escapeAttr(icon)}"></ha-icon><span>${this._escapeHtml(title)}</span></div>
        <div class="tile-value">${this._escapeHtml(value)}</div>
      </div>
    `;
  }

  _renderSwitch(entity, entityId, title, icon) {
    if (!entity || !entityId) {
      return '';
    }
    const active = entity.state === 'on';
    return `
      <button class="switch-tile ${active ? 'active' : ''}" data-action="toggle" data-entity="${this._escapeAttr(entityId)}">
        <ha-icon icon="${this._escapeAttr(icon)}"></ha-icon>
        <span>
          <span class="switch-title">${this._escapeHtml(title)}</span>
          <span class="switch-state">${active ? 'On' : 'Off'}</span>
        </span>
      </button>
    `;
  }

  _renderActions(runEntity, pauseEntity, stopEntity, isRunning, isPaused) {
    const buttons = [];
    if (!isRunning || isPaused) {
      buttons.push(this._renderAction(runEntity, isPaused ? 'Riprendi' : 'Avvia', 'mdi:play', 'start'));
    }
    if (isRunning && !isPaused) {
      buttons.push(this._renderAction(pauseEntity, 'Pausa', 'mdi:pause', 'pause'));
    }
    if (isRunning || isPaused) {
      buttons.push(this._renderAction(stopEntity, 'Stop', 'mdi:stop', 'stop'));
    }
    const html = buttons.filter(Boolean).join('');
    return html ? `<div class="actions">${html}</div>` : '';
  }

  _renderAction(entityId, label, icon, cssClass) {
    if (!entityId) {
      return '';
    }
    return `
      <button class="action-btn ${cssClass}" data-action="press" data-entity="${this._escapeAttr(entityId)}">
        <ha-icon icon="${this._escapeAttr(icon)}"></ha-icon>
        <span>${this._escapeHtml(label)}</span>
      </button>
    `;
  }

  _renderWarning(icon, text) {
    return `
      <div class="warning">
        <ha-icon icon="${this._escapeAttr(icon)}"></ha-icon>
        <span>${this._escapeHtml(text)}</span>
      </div>
    `;
  }

  _escapeHtml(value) {
    return String(value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  _escapeAttr(value) {
    return this._escapeHtml(value);
  }
}

customElements.define('samsung-dishwasher-card', SamsungDishwasherCard);
window.customCards = window.customCards || [];
window.customCards.push({
  type: 'samsung-dishwasher-card',
  name: 'Samsung Dishwasher Card',
  preview: true,
  description: 'Control card for Samsung SmartThings dishwashers',
});
