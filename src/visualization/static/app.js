// AiOpsBench Diagnosis Trace Viewer — type-dispatched rendering
// diagnostic_structure.type ∈ {linear, tree, graph}
(function () {
    'use strict';

    let currentTrace = null;
    let currentTraceFile = '';
    let traceList = [];
    let svg, rootGroup, zoom;
    let collapsedTurns = new Set();
    const collapsedTraceGroups = new Set();
    const traceGroupVisible = new Map();

    const TURN_W = 380, NODE_W = 340, NODE_H = 48, NODE_GAP = 10;
    const TURN_GAP = 32, TURN_PAD_X = 20, TURN_PAD_TOP = 44, TURN_PAD_BOT = 16;
    const COLLAPSED_H = 44;

    const GRAPH_TYPE_COLORS = {
        trigger: '#f87171', metric: '#60a5fa', experience: '#a78bfa',
        tool: '#4ade80', tag: '#fb923c', auxiliary: '#22d3ee'
    };

    document.addEventListener('DOMContentLoaded', init);

    function init() {
        svg = d3.select('#flowchart-svg');
        rootGroup = svg.select('#flowchart-root');
        zoom = d3.zoom().scaleExtent([0.05, 4])
            .on('zoom', (ev) => rootGroup.attr('transform', ev.transform));
        svg.call(zoom);

        document.getElementById('btn-fit').addEventListener('click', fitToScreen);
        document.getElementById('btn-expand-all').addEventListener('click', () => { collapsedTurns.clear(); render(); });
        document.getElementById('btn-collapse-all').addEventListener('click', () => {
            const turns = (currentTrace && currentTrace.turns) || [];
            turns.forEach((_, i) => collapsedTurns.add(i));
            render();
        });
        document.getElementById('btn-close-detail').addEventListener('click', closeDetail);
        initResize();
        loadTraceList();
    }

    async function loadTraceList() {
        const el = document.getElementById('trace-list');
        try {
            const resp = await fetch('/api/traces');
            const payload = await resp.json();
            traceList = payload.items;
            renderTraceList();
            const requested = new URLSearchParams(location.search).get('file');
            if (requested && traceList.some(trace => trace.filename === requested)) {
                onTraceSelected(requested);
            } else if (requested) {
                const selectedResponse = await fetch('/api/traces?q=' + encodeURIComponent(requested) + '&limit=1');
                const selectedPayload = await selectedResponse.json();
                if (selectedPayload.items.some(trace => trace.filename === requested)) {
                    traceList.unshift(selectedPayload.items[0]);
                    onTraceSelected(requested);
                }
            }
        } catch (e) {
            console.error('Failed to load traces:', e);
            el.textContent = 'Failed to load /api/traces';
        }
    }

    async function onTraceSelected(filename) {
        try {
            const resp = await fetch('/api/traces/' + encodeURIComponent(filename));
            currentTrace = await resp.json();
            currentTraceFile = filename;
            const url = new URL(location.href);
            url.searchParams.set('file', filename);
            history.replaceState(null, '', url);
            collapsedTurns.clear();
            closeDetail();
            renderMeta();
            renderBadge();
            renderTraceList();
            render();
            fitToScreen();
        } catch (err) {
            console.error('Failed to load trace:', err, err.stack);
        }
    }

    function renderTraceList() {
        const el = document.getElementById('trace-list');
        el.innerHTML = '';
        if (!traceList.length) {
            el.textContent = 'No trace files found';
            return;
        }

        const scenarios = new Map();
        sortedTraces().forEach(t => {
            const scenario = t.scenario || 'Unknown Scenario';
            const agent = t.agent_type || 'Unknown Agent';
            if (!scenarios.has(scenario)) scenarios.set(scenario, new Map());
            const agents = scenarios.get(scenario);
            if (!agents.has(agent)) agents.set(agent, []);
            agents.get(agent).push(t);
        });

        scenarios.forEach((agents, scenario) => {
            const scenarioKey = `scenario:${scenario}`;
            const scenarioBlock = document.createElement('div');
            scenarioBlock.className = 'trace-group';
            scenarioBlock.appendChild(groupHeader(scenario, countGroupItems(agents), scenarioKey));

            if (!collapsedTraceGroups.has(scenarioKey)) {
                agents.forEach((items, agent) => {
                    const agentKey = `${scenarioKey}:agent:${agent}`;
                    const agentBlock = document.createElement('div');
                    agentBlock.className = 'trace-agent-group';
                    agentBlock.appendChild(groupHeader(agent, items.length, agentKey));

                    if (!collapsedTraceGroups.has(agentKey)) {
                        const shown = traceGroupVisible.get(agentKey) || 5;
                        items.slice(0, shown).forEach(t => agentBlock.appendChild(traceItem(t)));
                        if (shown < items.length) agentBlock.appendChild(loadMoreButton(agentKey, items.length - shown));
                    }
                    scenarioBlock.appendChild(agentBlock);
                });
            }
            el.appendChild(scenarioBlock);
        });
    }

    function sortedTraces() {
        return traceList.slice().sort((a, b) => (b.timestamp || 0) - (a.timestamp || 0));
    }

    function countGroupItems(agents) {
        let total = 0;
        agents.forEach(items => { total += items.length; });
        return total;
    }

    function groupHeader(name, count, key) {
        const btn = document.createElement('button');
        btn.className = 'trace-group-header';
        btn.type = 'button';
        btn.innerHTML = `<span>${collapsedTraceGroups.has(key) ? '▶' : '▼'} ${escapeHtml(name)}</span><span>${count}</span>`;
        btn.addEventListener('click', () => {
            if (collapsedTraceGroups.has(key)) collapsedTraceGroups.delete(key);
            else collapsedTraceGroups.add(key);
            renderTraceList();
        });
        return btn;
    }

    function traceItem(trace) {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'trace-item' + (trace.filename === currentTraceFile ? ' active' : '');
        btn.innerHTML = `<span class="trace-time">${escapeHtml(formatTime(trace.timestamp))}</span>`
            + `<span class="trace-file">${escapeHtml(traceItemName(trace))}</span>`;
        btn.addEventListener('click', () => onTraceSelected(trace.filename));
        return btn;
    }

    function traceItemName(trace) {
        return trace.filename
            .replace(/\.json$/, '')
            .replace(/^run_?/, '')
            .replace(trace.scenario || '', '')
            .replace(trace.agent_type || '', '')
            .replace(/__+/g, '_')
            .replace(/^_+|_+$/g, '');
    }

    function loadMoreButton(key, remaining) {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'trace-more';
        btn.textContent = `Show 5 more (${remaining} left)`;
        btn.addEventListener('click', () => {
            traceGroupVisible.set(key, (traceGroupVisible.get(key) || 5) + 5);
            renderTraceList();
        });
        return btn;
    }

    function formatTime(ts) {
        return ts ? new Date(ts * 1000).toLocaleString() : 'No timestamp';
    }

    function structureType() {
        const s = currentTrace && currentTrace.diagnostic_structure;
        return (s && s.type) || 'linear';
    }

    function renderMeta() {
        const meta = currentTrace.metadata || {};
        const ev = currentTrace.evaluation || {};
        const el = document.getElementById('run-meta');
        const score = ev.total_score != null ? `Score: ${ev.total_score}` : '';
        const scenario = [meta.scenario_id, meta.case_id].filter(Boolean).join(' / ');
        const agent = meta.agent_type ? `${meta.agent_type}${meta.agent_mode ? '/' + meta.agent_mode : ''}` : '';
        el.textContent = [scenario, agent, score].filter(Boolean).join('  |  ');
    }

    function renderBadge() {
        const badge = document.getElementById('structure-badge');
        const t = structureType();
        badge.textContent = t;
        badge.className = 'structure-badge ' + t;
    }

    // ========== Render dispatch ==========

    function render() {
        if (!currentTrace) return;
        rootGroup.selectAll('*').remove();
        const t = structureType();
        if (t === 'tree') { renderTree(); }
        else if (t === 'graph') { renderGraph(); }
        else { renderLinear(); }
    }

    // ========== Linear renderer (turn chain) ==========

    function linearTurns() {
        return (currentTrace.turns || []).map(t => ({
            thinking: t.thinking || '',
            source: t.source || '',
            turn_number: t.turn_number,
            messages: t.messages || null,
            actions: (t.actions || []).map((a, ai) => ({
                api: a.api || 'action',
                args: a.args || {},
                result: (t.results || [])[ai] || null
            }))
        }));
    }

    function renderLinear() {
        hideSidePanel();
        const turns = linearTurns();
        let y = 20;
        const layouts = [];

        turns.forEach((turn, ti) => {
            const collapsed = collapsedTurns.has(ti);
            let h;
            if (collapsed) {
                h = COLLAPSED_H;
            } else {
                const nodeCount = (turn.thinking ? 1 : 0) + turn.actions.length * 2;
                h = TURN_PAD_TOP + nodeCount * (NODE_H + NODE_GAP) - NODE_GAP + TURN_PAD_BOT;
            }
            layouts.push({ ti, x: 20, y, w: TURN_W, h, collapsed, turn });
            y += h + TURN_GAP;
        });

        for (let i = 1; i < layouts.length; i++) {
            const prev = layouts[i - 1], curr = layouts[i];
            const x1 = prev.x + prev.w / 2;
            rootGroup.append('path').attr('class', 'edge')
                .attr('d', `M${x1},${prev.y + prev.h} L${x1},${curr.y}`)
                .attr('marker-end', 'url(#arrow)');
        }
        layouts.forEach(drawTurn);
    }

    function drawTurn(tl) {
        const { ti, x, y, w, h, collapsed, turn } = tl;
        const g = rootGroup.append('g').attr('transform', `translate(${x},${y})`);
        g.append('rect').attr('class', 'turn-bg').attr('width', w).attr('height', h).attr('rx', 8)
            .style('cursor', 'pointer')
            .on('click', (ev) => { showTurnDetail(ti, turn); });

        const btn = g.append('g').attr('class', 'turn-toggle')
            .attr('transform', 'translate(12, 14)').style('cursor', 'pointer');
        btn.append('text').attr('class', 'toggle-icon').text(collapsed ? '▶' : '▼');
        btn.on('click', (ev) => {
            ev.stopPropagation();
            if (collapsedTurns.has(ti)) collapsedTurns.delete(ti); else collapsedTurns.add(ti);
            render();
        });

        const summary = turn.actions.map(a => a.api).join(', ');
        g.append('text').attr('class', 'turn-label').attr('x', 30).attr('y', 27)
            .text(`Turn ${ti + 1}` + (collapsed ? `: ${truncate(summary, 35)}` : ''))
            .style('pointer-events', 'none');

        if (collapsed) return;

        let ny = TURN_PAD_TOP;
        if (turn.thinking) {
            drawSubNode(g, ny, 'thinking', 'Thinking', turn.thinking);
            ny += NODE_H + NODE_GAP;
        }
        turn.actions.forEach((action) => {
            drawSubNode(g, ny, 'action', action.api, action);
            ny += NODE_H + NODE_GAP;
            const res = action.result || {};
            drawSubNode(g, ny, 'result', res.status || 'result', res);
            ny += NODE_H + NODE_GAP;
        });
    }

    function drawSubNode(parentG, ny, type, label, content) {
        const g = parentG.append('g').attr('class', `node node-${type}`)
            .attr('transform', `translate(${TURN_PAD_X},${ny})`).style('cursor', 'pointer');
        g.append('rect').attr('width', NODE_W).attr('height', NODE_H).attr('rx', 6);
        g.append('text').attr('class', 'node-label').attr('x', 10).attr('y', 18).text(label);
        const desc = getDesc(type, content);
        if (desc) {
            g.append('text').attr('class', 'node-desc').attr('x', 10).attr('y', 36)
                .text(truncate(desc, 48));
        }
        g.on('click', (ev) => { ev.stopPropagation(); showDetail(type, label, content); });
    }

    function getDesc(type, content) {
        if (!content) return '';
        if (type === 'thinking') return typeof content === 'string' ? content : '';
        if (type === 'action') {
            const vals = Object.values(content.args || {}).map(v => typeof v === 'string' ? v : JSON.stringify(v));
            return vals.join(', ');
        }
        if (type === 'result') {
            if (content.status) return `status: ${content.status}`;
            if (content.data != null) return truncate(JSON.stringify(content.data), 80);
            return truncate(JSON.stringify(content), 80);
        }
        return '';
    }

    // ========== Tree renderer (DBot MCTS) ==========

    const TNODE_W = 240, TNODE_H = 56;

    function renderTree() {
        const struct = currentTrace.diagnostic_structure || {};
        const tree = struct.tree || { nodes: [], best_path: [] };
        const nodes = tree.nodes || [];
        if (!nodes.length) { renderLinear(); return; }

        const bestSet = new Set(tree.best_path || []);
        const byId = new Map(nodes.map(n => [n.id, n]));
        const rootNode = nodes.find(n => n.parent == null) || nodes[0];

        const root = d3.hierarchy(rootNode, (n) =>
            (n.children || []).map(cid => byId.get(cid)).filter(Boolean));

        const layout = d3.tree().nodeSize([TNODE_W + 24, TNODE_H + 60]);
        layout(root);

        const offsetX = 480, offsetY = 60;
        const link = d3.linkVertical().x(d => d.x + offsetX).y(d => d.y + offsetY);

        rootGroup.selectAll('path.tree-link').data(root.links()).enter()
            .append('path')
            .attr('class', d => {
                const onBest = bestSet.has(d.source.data.id) && bestSet.has(d.target.data.id);
                return 'tree-link' + (onBest ? ' best' : '') + (d.target.data.pruned ? ' pruned' : '');
            })
            .attr('d', link)
            .attr('marker-end', d => {
                const onBest = bestSet.has(d.source.data.id) && bestSet.has(d.target.data.id);
                return onBest ? 'url(#arrow-best)' : 'url(#arrow)';
            });

        const gNodes = rootGroup.selectAll('g.tree-node').data(root.descendants()).enter()
            .append('g')
            .attr('class', d => {
                const n = d.data;
                return 'tree-node node-' + (n.type === 'Action' ? 'action' : 'thinking')
                    + (n.pruned ? ' is-pruned' : '') + (bestSet.has(n.id) ? ' on-best' : '');
            })
            .attr('transform', d => `translate(${d.x + offsetX - TNODE_W / 2},${d.y + offsetY})`)
            .style('cursor', 'pointer')
            .on('click', (ev, d) => { ev.stopPropagation(); showTreeDetail(d.data, bestSet.has(d.data.id)); });

        gNodes.append('rect').attr('width', TNODE_W).attr('height', TNODE_H).attr('rx', 6);

        gNodes.append('text').attr('class', 'node-label').attr('x', 10).attr('y', 18)
            .text(d => `#${d.data.id} ${d.data.type}`);
        gNodes.append('text').attr('class', 'node-desc').attr('x', 10).attr('y', 36)
            .text(d => truncate(d.data.description || '', 30));
        gNodes.append('text').attr('class', 'meta-weight').attr('x', TNODE_W - 8).attr('y', 18)
            .text(d => d.data.weight != null ? `w:${(+d.data.weight).toFixed(2)}` : '');

        gNodes.each(function (d) {
            const n = d.data, g = d3.select(this);
            let bx = TNODE_W - 8;
            if (bestSet.has(n.id)) { bx -= 16; g.append('text').attr('class', 'meta-badge best-path').attr('x', bx).attr('y', 50).text('★'); }
            if (n.is_terminal) { bx -= 16; g.append('text').attr('class', 'meta-badge terminal').attr('x', bx).attr('y', 50).text('◉'); }
        });

        renderHypothesesPanel(struct.hypotheses || []);
    }

    function showTreeDetail(node, onBest) {
        const kv = { ID: node.id, Type: node.type, Weight: node.weight,
            'On Best Path': onBest ? 'Yes' : 'No', Terminal: node.is_terminal ? 'Yes' : 'No',
            Pruned: node.pruned ? 'Yes' : 'No' };
        openDetail(`Node #${node.id}`, (el) => {
            el.appendChild(makeKV(kv));
            if (node.description) el.appendChild(makeSection('Description', node.description));
            if (node.observation) el.appendChild(makeSection('Observation', formatJSON(node.observation)));
        });
    }

    function renderHypothesesPanel(hyps) {
        if (!hyps.length) { hideSidePanel(); return; }
        showSidePanel('Hypotheses', (el) => {
            hyps.forEach(h => {
                const card = document.createElement('div');
                card.className = 'hyp-card';
                const conf = h.confidence != null ? (h.confidence * 100).toFixed(0) + '%' : '';
                card.innerHTML =
                    `<div class="hyp-head"><span class="hyp-rc">${escapeHtml(h.root_cause || '')}</span>`
                    + `<span class="hyp-conf">${conf}</span></div>`
                    + `<div class="hyp-bar"><div class="hyp-bar-fill" style="width:${(h.confidence || 0) * 100}%"></div></div>`
                    + (h.rationale ? `<div class="hyp-rationale">${escapeHtml(h.rationale)}</div>` : '');
                if (h.evidence && h.evidence.length) {
                    const ul = document.createElement('ul');
                    ul.className = 'hyp-evidence';
                    h.evidence.forEach(e => { const li = document.createElement('li'); li.textContent = e; ul.appendChild(li); });
                    card.appendChild(ul);
                }
                el.appendChild(card);
            });
        });
    }

    // ========== Graph renderer (DBAIOps knowledge-graph evolution) ==========

    const GNODE_R = 30;

    function renderGraph() {
        const struct = currentTrace.diagnostic_structure || {};
        const evo = struct.evolution || {};
        const paths = evo.final_paths || evo.paths || [];

        // Merge all path nodes/edges into a deduplicated graph
        const nodeMap = new Map();
        const edges = [];
        if (struct.trigger) nodeMap.set(struct.trigger.id, Object.assign({}, struct.trigger));
        paths.forEach(p => {
            (p.nodes || []).forEach(n => { if (!nodeMap.has(n.id)) nodeMap.set(n.id, Object.assign({}, n)); });
            (p.edges || []).forEach(e => edges.push(Object.assign({ cross: false }, e)));
        });
        (evo.cross_edges || []).forEach(e => edges.push(Object.assign({ cross: true }, e)));

        const nodes = Array.from(nodeMap.values());
        if (!nodes.length) { renderLinear(); return; }

        // Assign depth via BFS from trigger for a layered layout
        const triggerId = struct.trigger ? struct.trigger.id : nodes[0].id;
        const adj = new Map();
        edges.forEach(e => {
            if (!adj.has(e.source)) adj.set(e.source, []);
            adj.get(e.source).push(e.target);
        });
        const depth = new Map([[triggerId, 0]]);
        const queue = [triggerId];
        while (queue.length) {
            const cur = queue.shift();
            (adj.get(cur) || []).forEach(t => {
                if (!depth.has(t)) { depth.set(t, depth.get(cur) + 1); queue.push(t); }
            });
        }
        nodes.forEach(n => { if (!depth.has(n.id)) depth.set(n.id, 0); });

        // Layered positions: x by depth, y stacked within each depth
        const byDepth = new Map();
        nodes.forEach(n => {
            const d = depth.get(n.id);
            if (!byDepth.has(d)) byDepth.set(d, []);
            byDepth.get(d).push(n);
        });
        const COL_W = 260, ROW_H = 110, OX = 80, OY = 80;
        const pos = new Map();
        byDepth.forEach((arr, d) => {
            arr.forEach((n, i) => pos.set(n.id, { x: OX + d * COL_W, y: OY + i * ROW_H }));
        });

        // Edges
        rootGroup.selectAll('path.graph-link').data(edges).enter().append('path')
            .attr('class', d => 'graph-link' + (d.cross ? ' cross' : ''))
            .attr('marker-end', 'url(#arrow)')
            .attr('d', d => {
                const s = pos.get(d.source), t = pos.get(d.target);
                if (!s || !t) return '';
                const mx = (s.x + t.x) / 2;
                return `M${s.x + GNODE_R},${s.y} C${mx},${s.y} ${mx},${t.y} ${t.x - GNODE_R},${t.y}`;
            });

        rootGroup.selectAll('text.edge-label').data(edges.filter(e => pos.get(e.source) && pos.get(e.target)))
            .enter().append('text').attr('class', 'edge-label')
            .attr('x', d => (pos.get(d.source).x + pos.get(d.target).x) / 2)
            .attr('y', d => (pos.get(d.source).y + pos.get(d.target).y) / 2 - 4)
            .text(d => d.type || '');

        // Nodes
        const gNodes = rootGroup.selectAll('g.graph-node').data(nodes).enter().append('g')
            .attr('class', 'graph-node').style('cursor', 'pointer')
            .attr('transform', d => { const p = pos.get(d.id); return `translate(${p.x},${p.y})`; })
            .on('click', (ev, d) => { ev.stopPropagation(); showGraphNodeDetail(d); });

        gNodes.append('circle').attr('r', GNODE_R)
            .attr('fill', d => (GRAPH_TYPE_COLORS[d.type] || '#888') + '33')
            .attr('stroke', d => GRAPH_TYPE_COLORS[d.type] || '#888');
        gNodes.append('text').attr('class', 'gnode-type').attr('text-anchor', 'middle').attr('y', -GNODE_R - 6)
            .text(d => d.type);
        gNodes.append('text').attr('class', 'gnode-name').attr('text-anchor', 'middle').attr('y', 4)
            .text(d => truncate(d.name || d.id, 12));

        // Render turn chain below the topology graph
        renderGraphTurnChain(pos, byDepth);

        renderEvolutionPanel(struct);
    }

    function renderGraphTurnChain(pos, byDepth) {
        const turns = currentTrace.turns || [];
        if (!turns.length) return;

        // Calculate Y offset: place turn chain below the topology graph
        let maxTopoY = 0;
        pos.forEach(p => { if (p.y > maxTopoY) maxTopoY = p.y; });
        const chainStartY = maxTopoY + GNODE_R + 80;

        // Section divider
        rootGroup.append('line')
            .attr('x1', 20).attr('x2', TURN_W + 60)
            .attr('y1', chainStartY - 30).attr('y2', chainStartY - 30)
            .attr('stroke', '#475569').attr('stroke-dasharray', '6,4');
        rootGroup.append('text')
            .attr('x', 20).attr('y', chainStartY - 40)
            .attr('class', 'gnode-type')
            .text('Diagnostic Steps (think → action → result)');

        let y = chainStartY;
        const layouts = [];
        turns.forEach((turn, ti) => {
            const collapsed = collapsedTurns.has(ti);
            let h;
            if (collapsed) {
                h = COLLAPSED_H;
            } else {
                const nodeCount = (turn.thinking ? 1 : 0) + (turn.actions || []).length * 2;
                h = TURN_PAD_TOP + nodeCount * (NODE_H + NODE_GAP) - NODE_GAP + TURN_PAD_BOT;
            }
            layouts.push({ ti, x: 20, y, w: TURN_W, h, collapsed, turn: mapGraphTurn(turn) });
            y += h + TURN_GAP;
        });

        for (let i = 1; i < layouts.length; i++) {
            const prev = layouts[i - 1], curr = layouts[i];
            const x1 = prev.x + prev.w / 2;
            rootGroup.append('path').attr('class', 'edge')
                .attr('d', `M${x1},${prev.y + prev.h} L${x1},${curr.y}`)
                .attr('marker-end', 'url(#arrow)');
        }
        layouts.forEach(drawTurn);
    }

    function mapGraphTurn(turn) {
        const sourceBadge = turn.source ? `[${turn.source}] ` : '';
        return {
            thinking: sourceBadge + (turn.thinking || ''),
            source: turn.source || '',
            turn_number: turn.turn_number,
            messages: turn.messages || null,
            actions: (turn.actions || []).map((a, ai) => ({
                api: a.api || 'action',
                args: a.args || {},
                result: (turn.results || [])[ai] || null
            }))
        };
    }

    function showGraphNodeDetail(node) {
        openDetail(node.name || node.id, (el) => {
            el.appendChild(makeKV({ ID: node.id, Type: node.type, Name: node.name }));
            if (node.content) el.appendChild(makeSection('Content', node.content));
        });
    }

    function renderEvolutionPanel(struct) {
        const evo = struct.evolution || {};
        const adf = evo.adf_results || [];
        const history = evo.history || [];
        showSidePanel('Graph Evolution', (el) => {
            const info = document.createElement('div');
            info.className = 'evo-info';
            info.innerHTML = `<span>depth: <b>${evo.depth != null ? evo.depth : '-'}</b>/${evo.max_depth || '-'}</span>`
                + `<span>paths: <b>${(evo.final_paths || evo.paths || []).length}</b></span>`
                + `<span>cross-edges: <b>${(evo.cross_edges || []).length}</b></span>`;
            el.appendChild(info);

            // Evolution history (per-depth ADF snapshots)
            if (history.length) {
                const hTitle = document.createElement('div');
                hTitle.className = 'side-section-title'; hTitle.textContent = 'Evolution History';
                el.appendChild(hTitle);
                history.forEach(h => {
                    const block = document.createElement('div');
                    block.className = 'evo-history-block';
                    const decision = h.should_continue ? 'continue' : 'terminate';
                    const decClass = h.should_continue ? 'evo-continue' : 'evo-terminate';
                    block.innerHTML = `<div class="evo-history-head">`
                        + `<span>Depth ${h.depth}</span>`
                        + `<span class="${decClass}">${decision}</span>`
                        + `<span class="evo-paths-count">${h.expanded_paths_count || 0} paths</span></div>`;
                    if (h.adf_results && h.adf_results.length) {
                        h.adf_results.forEach(r => {
                            const row = document.createElement('div');
                            row.className = 'adf-row' + (r.is_abnormal ? ' abnormal' : '');
                            const score = r.score != null ? r.score.toFixed(2) : '';
                            row.innerHTML = `<span class="adf-metric">${escapeHtml(r.metric)}</span>`
                                + `<span class="adf-bar"><span class="adf-bar-fill" style="width:${(r.score || 0) * 100}%"></span></span>`
                                + `<span class="adf-score">${score}</span>`;
                            block.appendChild(row);
                        });
                    }
                    el.appendChild(block);
                });
            }

            // Final ADF results (current state)
            if (adf.length) {
                const title = document.createElement('div');
                title.className = 'side-section-title'; title.textContent = 'Final ADF Results';
                el.appendChild(title);
                adf.forEach(r => {
                    const row = document.createElement('div');
                    row.className = 'adf-row' + (r.is_abnormal ? ' abnormal' : '');
                    const score = r.score != null ? r.score.toFixed(2) : '';
                    row.innerHTML = `<span class="adf-metric">${escapeHtml(r.metric)}</span>`
                        + `<span class="adf-bar"><span class="adf-bar-fill" style="width:${(r.score || 0) * 100}%"></span></span>`
                        + `<span class="adf-score">${score}</span>`;
                    el.appendChild(row);
                });
            }

            if (struct.diagnosis_report) {
                const title = document.createElement('div');
                title.className = 'side-section-title'; title.textContent = 'Diagnosis Report';
                el.appendChild(title);
                const rep = document.createElement('div');
                rep.className = 'diagnosis-report';
                rep.textContent = struct.diagnosis_report;
                el.appendChild(rep);
            }
        });
    }

    // ========== Detail panel (right, click-driven) ==========

    function openDetail(title, builder) {
        const panel = document.getElementById('detail-panel');
        const titleEl = document.getElementById('detail-title');
        const contentEl = document.getElementById('detail-content');
        panel.classList.remove('hidden');
        titleEl.textContent = title;
        contentEl.innerHTML = '';
        builder(contentEl);
    }

    function showDetail(type, label, content) {
        openDetail(label, (el) => {
            if (type === 'thinking') {
                el.appendChild(makeSection('Reasoning', typeof content === 'string' ? content : ''));
            } else if (type === 'action') {
                el.appendChild(makeKV({ API: content.api }));
                if (content.args && Object.keys(content.args).length) {
                    el.appendChild(makeSection('Arguments', formatJSON(content.args)));
                }
            } else if (type === 'result') {
                if (!content) return;
                if (content.status) el.appendChild(makeKV({ Status: content.status }));
                const data = content.data != null ? content.data : content;
                el.appendChild(makeSection('Data', formatJSON(data)));
            }
        });
    }

    function closeDetail() {
        document.getElementById('detail-panel').classList.add('hidden');
    }

    function showTurnDetail(ti, turn) {
        openDetail(`Turn ${ti + 1}`, (el) => {
            const kv = { Source: turn.source || 'linear', 'Turn Number': turn.turn_number != null ? turn.turn_number : ti + 1, Actions: turn.actions.map(a => a.api).join(', ') };
            el.appendChild(makeKV(kv));
            if (turn.messages && turn.messages.length) {
                const sec = document.createElement('div');
                sec.className = 'detail-section';
                const h = document.createElement('div');
                h.className = 'detail-section-title';
                h.textContent = `LLM Messages (${turn.messages.length})`;
                sec.appendChild(h);
                turn.messages.forEach((msg, mi) => {
                    const msgDiv = document.createElement('div');
                    msgDiv.className = 'turn-msg-item';
                    const role = document.createElement('span');
                    role.className = 'turn-msg-role turn-msg-role-' + (msg.role || 'unknown');
                    role.textContent = msg.role || 'unknown';
                    msgDiv.appendChild(role);
                    const content = document.createElement('pre');
                    content.className = 'turn-msg-content';
                    const raw = typeof msg.content === 'string' ? msg.content : JSON.stringify(msg.content, null, 2);
                    content.textContent = raw.length > 2000 ? raw.slice(0, 2000) + '...' : raw;
                    msgDiv.appendChild(content);
                    sec.appendChild(msgDiv);
                });
                el.appendChild(sec);
            }
        });
    }

    // ========== Side panel (left-docked, structure context) ==========

    function showSidePanel(title, builder) {
        const extra = document.getElementById('side-panel-extra');
        document.getElementById('side-panel-title').textContent = title;
        const content = document.getElementById('side-panel-content');
        content.innerHTML = '';
        builder(content);
        extra.classList.remove('hidden');
    }

    function hideSidePanel() {
        document.getElementById('side-panel-extra').classList.add('hidden');
    }

    // ========== Builders ==========

    function makeSection(title, text) {
        const div = document.createElement('div');
        div.className = 'detail-section';
        const h = document.createElement('div');
        h.className = 'detail-section-title';
        h.textContent = title;
        const pre = document.createElement('pre');
        pre.className = 'detail-pre';
        pre.textContent = text || '';
        div.appendChild(h);
        div.appendChild(pre);
        return div;
    }

    function makeKV(obj) {
        const div = document.createElement('div');
        div.className = 'detail-kv';
        Object.entries(obj).forEach(([k, v]) => {
            if (v == null) return;
            const row = document.createElement('div');
            row.className = 'kv-row';
            row.innerHTML = `<span class="kv-key">${escapeHtml(k)}</span><span class="kv-val">${escapeHtml(String(v))}</span>`;
            div.appendChild(row);
        });
        return div;
    }

    // ========== Utilities ==========

    function formatJSON(obj) {
        if (obj == null) return '';
        if (typeof obj === 'string') {
            try { return JSON.stringify(JSON.parse(obj), null, 2); } catch (_) { return obj; }
        }
        return JSON.stringify(obj, null, 2);
    }

    function escapeHtml(str) {
        if (str == null) return '';
        return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }

    function truncate(str, max) {
        if (!str) return '';
        return str.length > max ? str.slice(0, max) + '…' : str;
    }

    function fitToScreen() {
        const svgEl = document.getElementById('flowchart-svg');
        const node = rootGroup.node();
        if (!node) return;
        const bounds = node.getBBox();
        if (!bounds.width || !bounds.height) return;
        const pad = 40;
        // Reserve space for the left side panel when visible so nodes aren't occluded.
        const sidePanel = document.getElementById('side-panel');
        const contextPanel = document.getElementById('side-panel-extra');
        const leftReserve = sidePanel.offsetWidth + (contextPanel.classList.contains('hidden') ? 24 : contextPanel.offsetWidth + 56);
        const w = svgEl.clientWidth, h = svgEl.clientHeight;
        const avail = w - leftReserve;
        const scale = Math.min((avail - pad * 2) / bounds.width, (h - pad * 2) / bounds.height, 1.5);
        const tx = leftReserve + (avail - bounds.width * scale) / 2 - bounds.x * scale;
        const ty = (h - bounds.height * scale) / 2 - bounds.y * scale;
        svg.transition().duration(300)
            .call(zoom.transform, d3.zoomIdentity.translate(tx, ty).scale(scale));
    }

    function initResize() {
        const handle = document.getElementById('resize-handle');
        const panel = document.getElementById('detail-panel');
        handle.addEventListener('mousedown', (e) => {
            const startX = e.clientX, startW = panel.offsetWidth;
            const onMove = (ev) => { panel.style.width = Math.max(280, startW + (startX - ev.clientX)) + 'px'; };
            const onUp = () => { document.removeEventListener('mousemove', onMove); document.removeEventListener('mouseup', onUp); };
            document.addEventListener('mousemove', onMove);
            document.addEventListener('mouseup', onUp);
        });
    }

})();
