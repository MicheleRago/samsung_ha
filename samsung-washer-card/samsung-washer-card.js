console.info("%c SAMSUNG WASHER CARD %c v1.0.0 is loaded! ", "color: white; background: #1976d2; font-weight: 700;", "color: #1976d2; background: white; font-weight: 700;");

class SamsungWasherCard extends HTMLElement {
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
          display: flex;
          flex-direction: column;
          align-items: center;
          margin-bottom: 18px;
          text-align: center;
        }
        .hero-icon {
          width: 88px;
          height: 88px;
          border-radius: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
          margin-bottom: 12px;
          color: #1976d2;
          background: rgba(25, 118, 210, 0.14);
          filter: drop-shadow(0 8px 16px rgba(0,0,0,0.18));
          transition: all 0.3s ease;
        }
        .hero-icon ha-icon {
          --mdc-icon-size: 58px;
        }
        .hero.running .hero-icon {
          color: #00a6a6;
          background: rgba(0, 166, 166, 0.16);
          animation: drum-pulse 2s ease-in-out infinite;
        }
        .hero.paused .hero-icon {
          color: #f57c00;
          background: rgba(245, 124, 0, 0.16);
        }
        .hero.off .hero-icon,
        .hero.unavailable .hero-icon {
          color: var(--disabled-text-color, #9e9e9e);
          background: var(--secondary-background-color, rgba(120, 120, 120, 0.12));
          filter: none;
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
        .status-line {
          height: 4px;
          border-radius: 999px;
          margin-bottom: 16px;
          overflow: hidden;
          background: var(--divider-color, rgba(120, 120, 120, 0.24));
        }
        .status-line span {
          display: block;
          width: 100%;
          height: 100%;
          background: #1976d2;
        }
        .status-line.running span {
          background: linear-gradient(90deg, #1976d2, #00a6a6, #1976d2);
          animation: wash-flow 1.6s linear infinite;
          background-size: 220% 100%;
        }
        .status-line.paused span {
          background: #f57c00;
        }
        .status-line.off span,
        .status-line.unavailable span {
          background: var(--disabled-text-color, #9e9e9e);
        }
        .metrics {
          display: grid;
          grid-template-columns: repeat(2, minmax(0, 1fr));
          gap: 10px;
        }
        .metrics:not(:empty) {
          margin-bottom: 10px;
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
          background: rgba(25, 118, 210, 0.16);
        }
        .switch-tile ha-icon {
          --mdc-icon-size: 22px;
          color: var(--secondary-text-color);
          flex: 0 0 auto;
        }
        .switch-tile.active ha-icon {
          color: #1976d2;
        }
        .switch-title {
          display: block;
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
          gap: 16px;
          margin-top: 24px;
          flex-wrap: wrap;
        }
        .btn-action {
          display: flex;
          flex-direction: column;
          align-items: center;
          border: 0;
          background: none;
          color: var(--primary-text-color);
          cursor: pointer;
          font: inherit;
          font-weight: 600;
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
        .btn-action .icon-wrap ha-icon {
          --mdc-icon-size: 20px;
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
        .btn-action.pause .icon-wrap {
          background: var(--warning-color, #ff9800);
          color: white;
        }
        .btn-action.stop .icon-wrap {
          background: var(--error-color, #f44336);
          color: white;
          box-shadow: 0 4px 12px rgba(244, 67, 54, 0.3);
        }
        .btn-action.stop {
          color: #f44336;
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
          100% { background-position: 220% 0; }
        }
        @keyframes drum-pulse {
          0% { filter: drop-shadow(0 0 8px rgba(0,166,166,0.28)); }
          50% { filter: drop-shadow(0 0 18px rgba(0,166,166,0.48)); }
          100% { filter: drop-shadow(0 0 8px rgba(0,166,166,0.28)); }
        }
        @media (max-width: 420px) {
          ha-card {
            padding: 14px;
          }
          .hero-icon {
            width: 72px;
            height: 72px;
          }
          .hero-icon ha-icon {
            --mdc-icon-size: 46px;
          }
          .metrics,
          .option-grid {
            grid-template-columns: 1fr;
          }
          .btn-action {
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
    const door = getState('door');
    const power = getState('power');
    const remote = getState('remote_control');

    const machineState = this._state(machine);
    const jobState = this._state(job);
    const remainingValue = this._state(remaining);
    const completionValue = this._state(completion);
    const remoteState = this._state(remote);
    const doorOpen = this._isDoorOpen(this._state(door));
    const powerOff = power && this._state(power) === 'off';
    const remoteDisabled = !!remoteState && !this._isTruthy(remoteState);
    const isPaused = this._isPaused(machineState) || this._isPaused(jobState);
    const isActive = this._isActive(machineState, jobState) || isPaused;
    const isRunning = isActive && !isPaused;
    const isUnavailable = !machineState;
    const isComplete = this._isComplete(machineState, jobState);
    const isIdle = !isActive;
    const canConfigure = !isUnavailable && isIdle && !powerOff;
    const canStart = canConfigure && !doorOpen && !remoteDisabled;
    const statusClass = isUnavailable ? 'unavailable' : powerOff ? 'off' : isPaused ? 'paused' : isRunning ? 'running' : 'ready';

    const subtitleParts = [
      this._stateLabel(machineState),
      isActive ? this._jobLabel(jobState) : '',
      isActive ? this._formatDuration(remainingValue) : '',
    ].filter(Boolean);

    const progressTiles = [
      isActive ? this._renderMetric('Programma', this._courseLabel(course && course.state), 'mdi:tune-vertical') : '',
      isActive ? this._renderMetric('Fase', this._jobLabel(jobState), 'mdi:state-machine') : '',
      isActive ? this._renderMetric('Residuo', this._formatDuration(remainingValue), 'mdi:timer-outline') : '',
      isActive || isComplete ? this._renderMetric('Fine', this._formatDateTime(completionValue), 'mdi:clock-outline') : '',
    ].filter(Boolean).join('');

    const courseHtml = canConfigure && course && Array.isArray(course.attributes.options) ? `
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

    const optionTiles = canConfigure ? [
      this._renderSwitch(getState('child_lock'), entityId('child_lock'), 'Blocco bambini', 'mdi:lock-outline'),
    ].filter(Boolean).join('') : '';
    const powerTile = isIdle ? this._renderSwitch(power, entityId('power'), 'Power', 'mdi:power') : '';

    const runEntity = entityId('run_btn') || entityId('start_btn');
    const pauseEntity = entityId('pause_btn');
    const stopEntity = entityId('stop_btn');
    const actions = this._renderActions(runEntity, pauseEntity, stopEntity, isActive, isPaused, canStart);

    const warnings = [
      doorOpen ? this._renderWarning('mdi:door-open', 'Porta aperta') : '',
      powerOff ? this._renderWarning('mdi:power', 'Lavatrice spenta') : '',
      remoteDisabled && !powerOff ? this._renderWarning('mdi:remote-off', 'Smart Control non attivo') : '',
    ].filter(Boolean).join('');

    this.content.innerHTML = `
      <div class="hero ${statusClass}">
        <div class="hero-icon"><ha-icon icon="${this._escapeAttr(config.icon || 'mdi:washing-machine')}"></ha-icon></div>
        <div class="hero-title">${this._escapeHtml(config.name || 'Lavatrice Samsung')}</div>
        <div class="hero-subtitle">${this._escapeHtml(subtitleParts.join(' - ') || 'Stato non disponibile')}</div>
      </div>

      <div class="status-line ${statusClass}"><span></span></div>

      ${progressTiles ? `<div class="metrics">${progressTiles}</div>` : ''}
      ${courseHtml ? `<div class="metrics">${courseHtml}</div>` : ''}
      ${optionTiles || powerTile ? `<div class="option-grid">${optionTiles}${powerTile}</div>` : ''}
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

  _isActive(machineState, jobState) {
    const machine = String(machineState).toLowerCase();
    const job = String(jobState).toLowerCase();
    if (['run', 'running', 'wash', 'washing'].includes(machine)) {
      return true;
    }
    return !!job && !['ready', 'finish', 'finished', 'finito', 'none', 'idle', 'stop', 'stopped'].includes(job);
  }

  _isComplete(machineState, jobState) {
    const machine = String(machineState).toLowerCase();
    const job = String(jobState).toLowerCase();
    return ['finish', 'finished', 'finito'].includes(machine) || ['finish', 'finished', 'finito'].includes(job);
  }

  _stateLabel(value) {
    const labels = {
      ready: 'Pronta',
      run: 'In corso',
      running: 'In corso',
      wash: 'Lavaggio',
      washing: 'Lavaggio',
      pause: 'In pausa',
      paused: 'In pausa',
      stop: 'Ferma',
      stopped: 'Ferma',
      off: 'Spenta',
      on: 'Accesa',
      finish: 'Finito',
      finished: 'Finito',
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
      '01': 'Cotone',
      '02': 'Sintetici',
      '03': 'Lana',
      '04': 'A mano',
      '05': 'Quotidiano',
      '06': 'Rapido',
      '07': 'Intensivo a freddo',
      '0a': 'Biancheria letto',
      '0b': "Rapido 15'",
      '0c': 'Risciacquo + centrifuga',
      '0d': 'Centrifuga',
      '0e': 'Scarico/Centrifuga',
      '11': 'Pulizia cestello',
      '1c': 'Eco 40-60',
      '1d': 'Rapido lava+asciuga',
      '1e': 'Outdoor',
      '1f': 'Baby care',
      '21': 'Jeans',
      '2b': 'Active wear',
      '2c': 'Colorati',
      cotton: 'Cotone',
      synthetics: 'Sintetici',
      wool: 'Lana',
      quick: 'Rapido',
      rinse: 'Risciacquo',
      spin: 'Centrifuga',
      eco: 'Eco',
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
    const active = entity.state === 'on' || entity.state === 'locked';
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

  _renderActions(runEntity, pauseEntity, stopEntity, isActive, isPaused, canStart) {
    const buttons = [];
    if (isPaused || (!isActive && canStart)) {
      buttons.push(this._renderAction(runEntity, isPaused ? 'Riprendi' : 'Avvia', 'mdi:play', 'start'));
    }
    if (isActive && !isPaused) {
      buttons.push(this._renderAction(pauseEntity, 'Pausa', 'mdi:pause', 'pause'));
    }
    if (isActive || isPaused) {
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
      <button class="btn-action ${cssClass}" data-action="press" data-entity="${this._escapeAttr(entityId)}">
        <div class="icon-wrap"><ha-icon icon="${this._escapeAttr(icon)}"></ha-icon></div>
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

customElements.define('samsung-washer-card', SamsungWasherCard);
window.customCards = window.customCards || [];
window.customCards.push({
  type: 'samsung-washer-card',
  name: 'Samsung Washer Card',
  preview: true,
  description: 'Control card for Samsung SmartThings washers',
});
