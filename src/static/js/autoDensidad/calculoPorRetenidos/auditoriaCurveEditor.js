(function () {
    function getState() {
        return window.__auditoriaCurveEditorState || null;
    }

    function formatPercent(value) {
        return `${Number(value || 0).toFixed(2)}%`;
    }

    function clamp(value, min, max) {
        return Math.min(Math.max(value, min), max);
    }

    function buildStateMarkup(isInside) {
        const symbol = isInside ? '✓' : '✗';
        const color = isInside ? '#28a745' : '#dc3545';
        return `<strong style="color: ${color}">${symbol}</strong>`;
    }

    function updateVirtualTableRow(index) {
        const state = getState();
        if (!state || !state.grafico || !Array.isArray(state.grafico.pasante_virtual)) {
            return;
        }

        const currentValue = Number(state.grafico.pasante_virtual[index] || 0);
        const min = Number(state.grafico.banda_min[index] || 0);
        const max = Number(state.grafico.banda_max[index] || 0);
        const trigger = document.querySelector(`.curve-editor-trigger[data-curve-index="${index}"]`);
        const stateCell = document.querySelector(`.curve-editor-state-virtual[data-curve-index="${index}"]`);
        const isInside = currentValue >= min && currentValue <= max;

        if (trigger) {
            trigger.textContent = formatPercent(currentValue);
            trigger.dataset.value = String(currentValue);
        }

        if (stateCell) {
            stateCell.innerHTML = buildStateMarkup(isInside);
        }
    }

    function redrawCurves() {
        const state = getState();
        if (!state || typeof window.dibujarGrafico !== 'function') {
            return;
        }

        window.dibujarGrafico(state.grafico, state.entrada);

        if (typeof window.dibujarGraficosAnalisis === 'function') {
            window.dibujarGraficosAnalisis(state.grafico, state.entrada);
        }

        if (typeof window.recalcularVistaOperativaDesdeCurvaVirtual === 'function') {
            window.recalcularVistaOperativaDesdeCurvaVirtual();
        }
    }

    function closeEditor() {
        const host = document.getElementById('curveEditorHost');
        if (host) {
            host.innerHTML = '';
        }
    }

    function renderEditor(index) {
        const state = getState();
        const host = document.getElementById('curveEditorHost');
        if (!state || !host || !state.grafico || !Array.isArray(state.grafico.pasante_virtual)) {
            return;
        }

        const tamiz = state.grafico.tamices[index];
        const min = Number(state.grafico.banda_min[index] || 0);
        const max = Number(state.grafico.banda_max[index] || 0);
        const currentValue = Number(state.grafico.pasante_virtual[index] || 0);
        const valueForSlider = clamp(currentValue, min, max);

        host.innerHTML = `
            <div class="curve-editor-panel">
                <div class="curve-editor-panel-header">
                    <div>
                        <div class="curve-editor-panel-title">Ajustar pasante virtual</div>
                        <div class="curve-editor-panel-meta">Tamiz ${tamiz} mm | rango permitido ${formatPercent(min)} - ${formatPercent(max)}</div>
                    </div>
                    <div class="curve-editor-actions">
                        <button type="button" class="primary" data-action="consolidate">Consolidar ajuste</button>
                        <button type="button" data-action="reset">Restablecer</button>
                        <button type="button" data-action="close">Cerrar</button>
                    </div>
                </div>
                <div class="curve-editor-range-wrap">
                    <input
                        class="curve-editor-range"
                        type="range"
                        min="${min}"
                        max="${max}"
                        step="0.01"
                        value="${valueForSlider}"
                    />
                    <div class="curve-editor-values">
                        <span>${formatPercent(min)}</span>
                        <span class="curve-editor-current">${formatPercent(valueForSlider)}</span>
                        <span>${formatPercent(max)}</span>
                    </div>
                </div>
                <div class="curve-editor-feedback">Ajustá la curva y consolidá cuando el resultado quede listo para validar.</div>
            </div>
        `;

        const slider = host.querySelector('.curve-editor-range');
        const currentValueLabel = host.querySelector('.curve-editor-current');
        const consolidateButton = host.querySelector('[data-action="consolidate"]');
        const resetButton = host.querySelector('[data-action="reset"]');
        const closeButton = host.querySelector('[data-action="close"]');
        const originalValue = currentValue;

        const applyValue = (rawValue) => {
            const nextValue = clamp(Number(rawValue), min, max);
            state.grafico.pasante_virtual[index] = nextValue;
            currentValueLabel.textContent = formatPercent(nextValue);
            updateVirtualTableRow(index);
            redrawCurves();
        };

        slider.addEventListener('input', (event) => {
            applyValue(event.target.value);
        });

        resetButton.addEventListener('click', () => {
            const resetValue = clamp(originalValue, min, max);
            slider.value = String(resetValue);
            applyValue(resetValue);
        });

        if (consolidateButton) {
            consolidateButton.addEventListener('click', () => {
                if (typeof window.consolidarAjusteManual === 'function') {
                    window.consolidarAjusteManual();
                }
            });
        }

        closeButton.addEventListener('click', () => {
            closeEditor();
        });
    }

    function bindTrigger(trigger) {
        if (trigger.dataset.curveEditorBound === '1') {
            return;
        }

        trigger.dataset.curveEditorBound = '1';
        trigger.addEventListener('click', () => {
            const index = Number(trigger.dataset.curveIndex);
            if (Number.isFinite(index)) {
                renderEditor(index);
            }
        });
    }

    function init() {
        document.querySelectorAll('.curve-editor-trigger').forEach(bindTrigger);
    }

    window.AuditoriaCurveEditor = {
        init,
        close: closeEditor,
    };
})();
