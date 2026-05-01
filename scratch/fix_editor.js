    function createNodeElement(node) {
        const el = document.createElement('div');
        el.className = 'node';
        el.id = `node-el-${node.id}`;
        el.style.left = `${positions[node.id].x}px`;
        el.style.top = `${positions[node.id].y}px`;

        const header = document.createElement('div');
        header.className = 'node-header';
        header.innerHTML = `<span>#${node.id.split('_')[1]}</span> <span style="opacity: 0.5">@${node.offset}</span>`;
        
        header.onmousedown = (e) => {
            document.querySelectorAll('.node').forEach(n => n.classList.remove('selected'));
            el.classList.add('selected');
            selectedNodeId = node.id;
            
            let isDragging = true;
            const onMouseMove = (me) => {
                if (!isDragging) return;
                positions[node.id].x += me.movementX;
                positions[node.id].y += me.movementY;
                el.style.left = `${positions[node.id].x}px`;
                el.style.top = `${positions[node.id].y}px`;
                drawConnections();
            };
            const onMouseUp = () => {
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
        
        let currentSpeaker = "???";
        let currentPos = "중앙";
        
        node.commands.forEach((cmd) => {
            if (cmd.op === 'C0') { currentPos = cmd.text.replace('📍 위치: ', ''); }
            if (cmd.op === 'CC') { currentSpeaker = cmd.text.replace('👤 ', '').replace(' 등장', ''); }
            
            if (!cmd.significant && !['C8', 'AD', 'AC', 'DC'].includes(cmd.op)) return;

            const row = document.createElement('div');
            row.className = 'story-row';
            
            if (cmd.op === 'C8') { // Dialogue
                const textEl = document.createElement('div');
                textEl.className = 'story-text';
                textEl.innerText = cmd.text.replace('💬 ', '').replace(/"/g, '');
                textEl.onclick = (e) => {
                    const input = document.createElement('textarea');
                    input.value = textEl.innerText;
                    input.className = 'story-input';
                    input.onblur = () => {
                        textEl.innerText = input.value;
                        cmd.text = `💬 "${input.value}"`;
                        input.remove();
                    };
                    textEl.innerHTML = '';
                    textEl.appendChild(input);
                    input.focus();
                    e.stopPropagation();
                };

                row.innerHTML = `
                    <div class="speaker-icon" style="background: ${currentSpeaker.includes('카탈리나') ? '#f7768e' : '#7aa2f7'}"></div>
                    <div class="story-content">
                        <div class="story-header"><span>${currentSpeaker}</span> <span>${currentPos}</span></div>
                    </div>
                `;
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
