window.initEventEditor = () => {
    let nodes = {};
    let positions = {};
    let selectedNodeId = null;
    let undoStack = [];
    let redoStack = [];
    
    const nodeLayer = document.getElementById('event-node-layer');
    const svgLayer = document.getElementById('event-svg-layer');
    if (!nodeLayer || !svgLayer) return;

    function pushHistory() {
        undoStack.push(JSON.stringify({ nodes, positions }));
        if (undoStack.length > 50) undoStack.shift();
        redoStack = []; // Clear redo on new action
    }

    window.undo = () => {
        if (undoStack.length === 0) return;
        redoStack.push(JSON.stringify({ nodes, positions }));
        const state = JSON.parse(undoStack.pop());
        nodes = state.nodes;
        positions = state.positions;
        render(false); // Don't push to history during undo
    };

    window.redo = () => {
        if (redoStack.length === 0) return;
        undoStack.push(JSON.stringify({ nodes, positions }));
        const state = JSON.parse(redoStack.pop());
        nodes = state.nodes;
        positions = state.positions;
        render(false);
    };

    const OPCODE_MAP = {
        'C0': '창 위치',
        'CC': '초상화',
        'C8': '대사',
        'C7': '클릭 대기',
        'AD': '조건 분기',
        'AC': '조건 체크',
        'DC': '이동',
        '0F': '상태 설정',
    };

    async function loadScenario(path) {
        console.log("Loading scenario:", path);
        try {
            const res = await fetch(`/api/scenario/${path}`);
            const data = await res.json();
            if (data.error) {
                console.error("Server error:", data.error);
                return;
            }
            nodes = data;
            console.log("Loaded nodes count:", Object.keys(nodes).length);
            
            const nodeIds = Object.keys(nodes);
            nodeIds.forEach((id, idx) => {
                positions[id] = { 
                    x: 80 + (idx % 4) * 260, 
                    y: 80 + Math.floor(idx / 4) * 450 
                };
            });
            render(false);
        } catch (err) {
            console.error("Failed to load scenario", err);
        }
    }

    function render(push = true) {
        if (push) pushHistory();
        console.log("Rendering...");
        if (!nodeLayer) return;
        nodeLayer.innerHTML = '';
        for (const id in nodes) {
            createNodeElement(nodes[id]);
        }
        drawConnections();
    }

    function createNodeElement(node) {
        const el = document.createElement('div');
        el.className = 'node';
        el.id = `node-el-${node.id}`;
        el.style.left = `${positions[node.id].x}px`;
        el.style.top = `${positions[node.id].y}px`;

        const header = document.createElement('div');
        header.className = 'node-header';
        header.innerHTML = `
            <span>#${node.id.split('_')[1]}</span>
            <div class="node-controls">
                <button class="node-link-btn" title="Link/Unlink another node">🔗 Link</button>
                <button class="node-unlink-btn" title="Clear all links">🚫 Unlink</button>
                <button class="node-del-btn" title="Delete node">❌</button>
                <span style="opacity: 0.5">@${node.offset}</span>
            </div>
        `;

        header.querySelector('.node-link-btn').onclick = (e) => {
            e.stopPropagation();
            alert("연결하거나 끊을 대상 노드를 클릭하세요!");
            window.linkSourceNodeId = node.id;
        };

        header.querySelector('.node-unlink-btn').onclick = (e) => {
            e.stopPropagation();
            if (confirm("이 노드에서 나가는 모든 연결을 삭제할까요?")) {
                pushHistory();
                node.next_nodes = [];
                render(false);
            }
        };

        header.querySelector('.node-del-btn').onclick = (e) => {
            e.stopPropagation();
            if (confirm("이 노드를 삭제하시겠습니까?")) {
                pushHistory();
                delete nodes[node.id];
                render(false);
            }
        };
        
        el.onclick = () => {
            if (window.linkSourceNodeId && window.linkSourceNodeId !== node.id) {
                pushHistory();
                const sourceNode = nodes[window.linkSourceNodeId];
                const idx = sourceNode.next_nodes.indexOf(node.id);
                if (idx > -1) {
                    sourceNode.next_nodes.splice(idx, 1); // Remove if exists
                } else {
                    sourceNode.next_nodes.push(node.id); // Add if new
                }
                render(false);
                window.linkSourceNodeId = null;
            }
        };
        header.onmousedown = (e) => {
            document.querySelectorAll('.node').forEach(n => n.classList.remove('selected'));
            el.classList.add('selected');
            selectedNodeId = node.id;
            
            let isDragging = true;
            const startPos = { x: positions[node.id].x, y: positions[node.id].y };

            const onMouseMove = (me) => {
                if (!isDragging) return;
                positions[node.id].x += me.movementX;
                positions[node.id].y += me.movementY;
                el.style.left = `${positions[node.id].x}px`;
                el.style.top = `${positions[node.id].y}px`;
                drawConnections();
            };
            const onMouseUp = () => {
                if (isDragging) {
                    if (startPos.x !== positions[node.id].x || startPos.y !== positions[node.id].y) {
                        const currentPos = { x: positions[node.id].x, y: positions[node.id].y };
                        positions[node.id] = startPos;
                        pushHistory();
                        positions[node.id] = currentPos;
                    }
                }
                isDragging = false;
                window.removeEventListener('mousemove', onMouseMove);
                window.removeEventListener('mouseup', onMouseUp);
            };
            window.addEventListener('mousemove', onMouseMove);
            window.addEventListener('mouseup', onMouseUp);
            e.stopPropagation();
        };

        const body = document.createElement('div');
        body.className = 'node-body';
        
        let currentSpeaker = document.getElementById('scenario-select').value.startsWith('2') ? "카탈리나" : "???";
        let currentPos = "중앙";
        
        node.commands.forEach((cmd) => {
            if (cmd.op === 'C0') { currentPos = cmd.text.replace('📍 위치: ', ''); return; }
            if (cmd.op === 'CC') { currentSpeaker = cmd.text.replace('👤 ', '').replace(' 등장', ''); return; }
            
            if (!cmd.significant && !['C8', 'AD', 'AC', 'DC'].includes(cmd.op)) return;

            const row = document.createElement('div');
            row.className = 'story-row';
            
            if (cmd.op === 'C8') {
                const textEl = document.createElement('div');
                textEl.className = 'story-text';
                textEl.innerText = cmd.text.replace('💬 ', '').replace(/"/g, '');
                textEl.onclick = (e) => {
                    const input = document.createElement('textarea');
                    input.value = textEl.innerText;
                    input.className = 'story-input';
                    input.onblur = () => {
                        if (textEl.innerText !== input.value) {
                            pushHistory();
                            textEl.innerText = input.value;
                            cmd.text = `💬 "${input.value}"`;
                        }
                        input.remove();
                    };
                    textEl.innerHTML = '';
                    textEl.appendChild(input);
                    input.focus();
                    e.stopPropagation();
                };

                const speakerEl = document.createElement('span');
                speakerEl.innerText = currentSpeaker;
                speakerEl.className = 'speaker-name-label';
                speakerEl.onclick = async (e) => {
                    e.stopPropagation();
                    
                    const res = await fetch('/api/characters');
                    window.characterList = await res.json();

                    const menu = document.createElement('div');
                    menu.className = 'character-menu glass-panel';
                    menu.style.position = 'fixed';
                    menu.style.left = `${e.clientX}px`;
                    menu.style.top = `${e.clientY}px`;
                    menu.style.zIndex = 10000;
                    
                    const searchInput = document.createElement('input');
                    searchInput.type = 'text';
                    searchInput.placeholder = '인물 검색...';
                    searchInput.className = 'menu-search-input';
                    searchInput.onclick = (se) => se.stopPropagation();
                    menu.appendChild(searchInput);

                    const listContainer = document.createElement('div');
                    listContainer.className = 'menu-list-container';
                    
                    const renderItems = (filter = '') => {
                        listContainer.innerHTML = '';
                        Object.entries(window.characterList).forEach(([id, name]) => {
                            if (filter && !name.includes(filter)) return;
                            const item = document.createElement('div');
                            item.className = 'menu-item';
                            item.innerText = name;
                            item.onclick = (ie) => {
                                ie.stopPropagation();
                                pushHistory();
                                speakerEl.innerText = name;
                                node.commands.forEach(c => {
                                    if (c.op === 'CC') {
                                        c.text = `👤 ${name} 등장`;
                                    }
                                });
                                currentSpeaker = name;
                                render(false);
                                menu.remove();
                            };
                            listContainer.appendChild(item);
                        });
                    };

                    searchInput.oninput = (se) => renderItems(se.target.value);
                    renderItems();
                    menu.appendChild(listContainer);

                    document.body.appendChild(menu);
                    searchInput.focus();
                    
                    const closeMenu = () => { menu.remove(); window.removeEventListener('click', closeMenu); };
                    setTimeout(() => window.addEventListener('click', closeMenu), 10);
                };

                row.innerHTML = `
                    <div class="speaker-icon" style="background: ${currentSpeaker.includes('카탈리나') ? '#f7768e' : '#7aa2f7'}"></div>
                    <div class="story-content">
                        <div class="story-header"></div>
                    </div>
                `;
                const header = row.querySelector('.story-header');
                header.appendChild(speakerEl);
                
                const posEl = document.createElement('span');
                posEl.innerText = ` ${currentPos}`;
                posEl.style.opacity = '0.5';
                posEl.style.marginLeft = '5px';
                header.appendChild(posEl);
                row.querySelector('.story-content').appendChild(textEl);
            } else if (['AD', 'AC', 'DC'].includes(cmd.op)) {
                row.classList.add('action-row');
                const target = node.next_nodes[0] ? node.next_nodes[0].split('_')[1] : '???';
                row.innerHTML = `
                    <div class="story-content">
                        <div class="action-text">${cmd.text.replace('node_id', '#' + target)}</div>
                    </div>
                `;
            }
            if (row.innerHTML) body.appendChild(row);
        });

        el.appendChild(header);
        el.appendChild(body);
        nodeLayer.appendChild(el);
    }

    function drawConnections() {
        svgLayer.innerHTML = '';
        const defs = document.createElementNS("http://www.w3.org/2000/svg", "defs");
        defs.innerHTML = `<marker id="arrow" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#3d59a1"/></marker>`;
        svgLayer.appendChild(defs);

        for (const id in nodes) {
            const node = nodes[id];
            node.next_nodes.forEach(nextId => {
                if (positions[nextId]) {
                    const start = positions[id];
                    const end = positions[nextId];
                    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
                    const sx = start.x + 190, sy = start.y + 20;
                    const ex = end.x, ey = end.y + 20;
                    const d = `M ${sx} ${sy} C ${sx + 40} ${sy} ${ex - 40} ${ey} ${ex} ${ey}`;
                    path.setAttribute("d", d);
                    path.setAttribute("stroke", "#3d59a1");
                    path.setAttribute("stroke-width", "1.5");
                    path.setAttribute("fill", "none");
                    path.setAttribute("marker-end", "url(#arrow)");
                    svgLayer.appendChild(path);
                }
            });
        }
    }

    document.getElementById('scenario-select').addEventListener('change', (e) => {
        loadScenario(e.target.value);
    });

    document.getElementById('add-node-btn').onclick = () => {
        pushHistory();
        const newId = `node_NEW_${Date.now()}`;
        nodes[newId] = {
            id: newId,
            offset: -1,
            commands: [
                { op: 'C0', text: '📍 위치: 중앙', significant: false },
                { op: 'CC', text: '👤 카탈리나 등장', significant: false },
                { op: 'C8', text: '💬 "새로운 대사를 입력하세요."', significant: true }
            ],
            next_nodes: []
        };
        positions[newId] = { x: 100, y: 100 };
        render(false);
        console.log("Added new node:", newId);
    };

    document.getElementById('refresh-event-btn').onclick = () => {
        loadScenario(document.getElementById('scenario-select').value);
    };

    document.getElementById('save-event-btn').onclick = async () => {
        const path = document.getElementById('scenario-select').value;
        const res = await fetch(`/api/scenario/${path}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(nodes)
        });
        if (res.ok) alert("Scenario saved successfully!");
        else alert("Failed to save scenario.");
    };

    document.getElementById('undo-btn').onclick = () => window.undo();
    document.getElementById('redo-btn').onclick = () => window.redo();

    window.addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.key === 'z') { e.preventDefault(); window.undo(); }
        if (e.ctrlKey && e.key === 'y') { e.preventDefault(); window.redo(); }
    });

    loadScenario('1/0');
};

window.addEventListener('DOMContentLoaded', () => {
    window.initEventEditor();
});
