import re

def update_file():
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace loadAdminPartySettings
    old_load_admin = """        function loadAdminPartySettings() {
            const grid = document.getElementById('partySettingsGrid');
            grid.innerHTML = '';
            Object.keys(partyIcons).forEach(partyId => {
                const item = document.createElement('div');
                item.className = 'party-setting-item';
                item.innerHTML = `
                    <div class="p-icon">${partyIcons[partyId]}</div>
                    <div style="font-size: 0.8em; color: #888; width: 45px;">${partyId}</div>
                    <input type="text" id="input_${partyId.replace(/ /g, '')}" value="${customPartyNames[partyId] || partyId}" placeholder="ชื่อพรรค">
                `;
                grid.appendChild(item);
            });
        }"""
        
    new_load_admin = """        let adminEditingParties = {}; 

        async function compressImage(file, maxSizeKB = 100) {
            return new Promise((resolve) => {
                const reader = new FileReader();
                reader.onload = (e) => {
                    const img = new Image();
                    img.onload = () => {
                        const canvas = document.createElement('canvas');
                        let width = img.width;
                        let height = img.height;
                        const maxDim = 300;
                        if (width > height && width > maxDim) {
                            height *= maxDim / width; width = maxDim;
                        } else if (height > maxDim) {
                            width *= maxDim / height; height = maxDim;
                        }
                        canvas.width = width;
                        canvas.height = height;
                        const ctx = canvas.getContext('2d');
                        ctx.drawImage(img, 0, 0, width, height);
                        resolve(canvas.toDataURL('image/jpeg', 0.8));
                    };
                    img.src = e.target.result;
                };
                reader.readAsDataURL(file);
            });
        }

        function loadAdminPartySettings() {
            adminEditingParties = JSON.parse(JSON.stringify(partyConfig));
            renderAdminPartyGrid();
        }

        function renderAdminPartyGrid() {
            const grid = document.getElementById('partySettingsGrid');
            grid.innerHTML = '';
            Object.values(adminEditingParties).forEach(p => {
                const item = document.createElement('div');
                item.className = 'party-setting-item';
                
                let previewHtml = p.imageUrl 
                    ? `<img src="${p.imageUrl}">` 
                    : `<span>${p.icon || '🗳️'}</span>`;

                item.innerHTML = `
                    <label class="p-img-preview" title="คลิกเพื่ออัปโหลดรูป" style="color:${p.color}; border-color:${p.color};">
                        ${previewHtml}
                        <input type="file" accept="image/*" class="party-img-input" data-id="${p.id}">
                    </label>
                    <input type="color" value="${p.color || '#667eea'}" class="party-color-input" data-id="${p.id}" title="สีพรรค">
                    <input type="text" value="${p.name}" class="party-name-input" data-id="${p.id}" placeholder="ชื่อพรรค">
                    <button class="btn-delete-party" data-id="${p.id}" title="ลบพรรค">ลบ</button>
                `;
                grid.appendChild(item);
            });
            
            grid.querySelectorAll('.party-name-input').forEach(input => {
                input.addEventListener('input', (e) => { adminEditingParties[e.target.dataset.id].name = e.target.value; });
            });
            grid.querySelectorAll('.party-color-input').forEach(input => {
                input.addEventListener('input', (e) => { 
                    adminEditingParties[e.target.dataset.id].color = e.target.value; 
                    e.target.previousElementSibling.style.borderColor = e.target.value;
                    e.target.previousElementSibling.style.color = e.target.value;
                });
            });
            grid.querySelectorAll('.party-img-input').forEach(input => {
                input.addEventListener('change', async (e) => {
                    const file = e.target.files[0];
                    if(file) {
                        const base64 = await compressImage(file);
                        adminEditingParties[e.target.dataset.id].imageUrl = base64;
                        renderAdminPartyGrid();
                    }
                });
            });
            grid.querySelectorAll('.btn-delete-party').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    if (confirm(`ต้องการลบใช่หรือไม่?`)) {
                        delete adminEditingParties[e.target.dataset.id];
                        renderAdminPartyGrid();
                    }
                });
            });
        }"""
        
    content = content.replace(old_load_admin, new_load_admin)

    # 2. Add listener for 'btnAddParty'
    old_init = """        // ===== PARTY SELECTION ====="""
    new_init = """        document.getElementById('btnAddParty').addEventListener('click', () => {
            const newId = 'party_' + Date.now();
            adminEditingParties[newId] = {
                id: newId, name: 'พรรคใหม่', icon: '❓', color: '#667eea', imageUrl: ''
            };
            renderAdminPartyGrid();
        });
        
        // ===== PARTY SELECTION ====="""
    content = content.replace(old_init, new_init)

    # 3. Replace partyIcons and saving logic
    old_partyIcons = """        // ===== PARTY ICON MAP =====
        const partyIcons = {
            'พรรค A': '🔴', 'พรรค B': '🔵', 'พรรค C': '🟢',
            'พรรค D': '🟡', 'พรรค E': '🟣', 'พรรค F': '🟠'
        };"""
    new_partyIcons = """        // ===== PARTY CONFIG =====
        let partyConfig = {
            'พรรค A': { id: 'พรรค A', name: 'พรรค A', icon: '🔴', color: '#f87171', imageUrl: '' },
            'พรรค B': { id: 'พรรค B', name: 'พรรค B', icon: '🔵', color: '#60a5fa', imageUrl: '' },
            'พรรค C': { id: 'พรรค C', name: 'พรรค C', icon: '🟢', color: '#4ade80', imageUrl: '' },
            'พรรค D': { id: 'พรรค D', name: 'พรรค D', icon: '🟡', color: '#facc15', imageUrl: '' },
            'พรรค E': { id: 'พรรค E', name: 'พรรค E', icon: '🟣', color: '#c084fc', imageUrl: '' },
            'พรรค F': { id: 'พรรค F', name: 'พรรค F', icon: '🟠', color: '#fb923c', imageUrl: '' }
        };
        
        function renderPartyGrid() {
            const grid = document.getElementById('partyGrid');
            if(!grid) return;
            grid.innerHTML = '';
            Object.values(partyConfig).forEach(p => {
                const card = document.createElement('div');
                card.className = 'party-card';
                card.dataset.party = p.id;
                
                let iconHtml = p.imageUrl 
                    ? `<img src="${p.imageUrl}" alt="${p.name}">`
                    : `<span>${p.icon || '🗳️'}</span>`;
                    
                card.innerHTML = `
                    <div class="party-icon" style="color: ${p.color}; border: 2px solid ${p.color}33;">${iconHtml}</div>
                    <div class="party-name">${p.name}</div>
                `;
                
                card.addEventListener('click', () => {
                    document.querySelectorAll('.party-card').forEach(c => c.classList.remove('selected'));
                    card.classList.add('selected');
                    selectedParty = p.id;
                });
                grid.appendChild(card);
            });
        }"""
    content = content.replace(old_partyIcons, new_partyIcons)

    # Replace openConfirmModal
    old_open_confirm = """        function openConfirmModal(partyName) {
            modalPartyIcon.textContent = partyIcons[partyName] || '🗳️';
            modalPartyName.textContent = customPartyNames[partyName] || partyName;
            modalOverlay.classList.add('show');
            modalConfirm.disabled = false;
            modalConfirm.textContent = '✅ ยืนยัน';
        }"""
    new_open_confirm = """        function openConfirmModal(partyId) {
            const p = partyConfig[partyId];
            if (p && p.imageUrl) {
                modalPartyIcon.innerHTML = `<img src="${p.imageUrl}" style="width:100%;height:100%;object-fit:cover;border-radius:50%;">`;
                modalPartyIcon.style.borderColor = p.color;
            } else {
                modalPartyIcon.innerHTML = p ? (p.icon || '🗳️') : '🗳️';
                if(p) modalPartyIcon.style.borderColor = p.color;
            }
            modalPartyName.textContent = p ? p.name : partyId;
            modalOverlay.classList.add('show');
            modalConfirm.disabled = false;
            modalConfirm.textContent = '✅ ยืนยัน';
        }"""
    content = content.replace(old_open_confirm, new_open_confirm)
    
    # Replace openSuccessModal
    old_success = """        function openSuccessModal(partyName) {
            successPartyIcon.textContent = partyIcons[partyName] || '🗳️';
            successPartyName.textContent = customPartyNames[partyName] || partyName;
            successModal.classList.add('show');
        }"""
    new_success = """        function openSuccessModal(partyId) {
            const p = partyConfig[partyId];
            if (p && p.imageUrl) {
                successPartyIcon.innerHTML = `<img src="${p.imageUrl}" style="width:28px;height:28px;object-fit:cover;border-radius:50%;display:inline-block;">`;
            } else {
                successPartyIcon.innerHTML = p ? (p.icon || '🗳️') : '🗳️';
            }
            successPartyName.textContent = p ? p.name : partyId;
            successModal.classList.add('show');
        }"""
    content = content.replace(old_success, new_success)

    # Save logic replacing old `setDoc(doc(db, 'config', 'parties')`
    old_save = """        document.getElementById('savePartyNames').addEventListener('click', async () => {
            const btn = document.getElementById('savePartyNames');
            btn.disabled = true;
            btn.textContent = '⏳ กำลังบันทึก...';
            
            const newNames = {};
            Object.keys(partyIcons).forEach(partyId => {
                const inputEl = document.getElementById('input_' + partyId.replace(/ /g, ''));
                if (inputEl) {
                    newNames[partyId] = inputEl.value.trim() || partyId; // default to original if empty
                }
            });
            
            try {
                await setDoc(doc(db, 'config', 'parties'), newNames);
                showToast('บันทึกชื่อพรรคเรียบร้อยแล้ว', 'success');
            } catch (err) {
                showToast('เกิดข้อผิดพลาด: ' + err.message, 'error');
            } finally {
                btn.disabled = false;
                btn.textContent = '💾 บันทึกชื่อพรรค';
            }
        });"""
    new_save = """        document.getElementById('savePartyNames').addEventListener('click', async () => {
            const btn = document.getElementById('savePartyNames');
            btn.disabled = true; btn.textContent = '⏳ กำลังบันทึก...';
            try {
                await setDoc(doc(db, 'config', 'partyDetails'), { parties: adminEditingParties });
                showToast('บันทึกการตั้งค่าพรรคเรียบร้อย', 'success');
            } catch (err) {
                showToast('เกิดข้อผิดพลาด: ' + err.message, 'error');
            } finally {
                btn.disabled = false; btn.textContent = '💾 บันทึกการตั้งค่าพรรค';
            }
        });"""
    content = content.replace(old_save, new_save)
    
    # Init config snapshot
    old_snap = """        console.log('P.TECH Vote 69 initialized');
        let customPartyNames = {
            'พรรค A': 'พรรค A', 'พรรค B': 'พรรค B', 'พรรค C': 'พรรค C',
            'พรรค D': 'พรรค D', 'พรรค E': 'พรรค E', 'พรรค F': 'พรรค F'
        };

        onSnapshot(doc(db, 'config', 'parties'), (docSnap) => {
            if (docSnap.exists()) {
                customPartyNames = { ...customPartyNames, ...docSnap.data() };
                document.querySelectorAll('.party-card').forEach(card => {
                    const partyId = card.dataset.party;
                    const nameEl = card.querySelector('.party-name');
                    if (nameEl && customPartyNames[partyId]) {
                        nameEl.textContent = customPartyNames[partyId];
                    }
                });
            }
        });"""
    new_snap = """        console.log('P.TECH Vote 69 initialized');
        
        // Initial render
        renderPartyGrid();

        onSnapshot(doc(db, 'config', 'partyDetails'), (docSnap) => {
            if (docSnap.exists() && docSnap.data().parties) {
                partyConfig = docSnap.data().parties;
            }
            renderPartyGrid();
            if (document.getElementById('adminPanel').classList.contains('active')) {
                loadAdminPartySettings();
            }
        });"""
    content = content.replace(old_snap, new_snap)
    
    # Party card selection removal - remove old party loop because renderPartyGrid does it
    old_party_click = """        document.querySelectorAll('.party-card').forEach(card => {
            card.addEventListener('click', () => {
                document.querySelectorAll('.party-card').forEach(c => c.classList.remove('selected'));
                card.classList.add('selected');
                selectedParty = card.dataset.party;
            });
        });"""
    content = content.replace(old_party_click, "")
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)
        
update_file()
