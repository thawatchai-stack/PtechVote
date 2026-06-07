import sys

with open("results.html", "r", encoding="utf-8") as f:
    text = f.read()

# 1. CSS
css_old = """.flash { animation: flashGold 0.8s ease-out; }
    </style>"""
css_new = """        /* ===== MODAL ===== */
        .modal {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.8); backdrop-filter: blur(5px);
            display: flex; align-items: center; justify-content: center;
            opacity: 0; pointer-events: none; transition: opacity 0.3s; z-index: 1000;
        }
        .modal.show { opacity: 1; pointer-events: auto; }
        .modal-box {
            background: var(--surface); border: 1px solid var(--border); border-radius: 20px;
            padding: 30px; width: 400px; max-width: 90%; text-align: center;
            transform: translateY(20px); transition: transform 0.3s;
        }
        .modal.show .modal-box { transform: translateY(0); }

        /* ===== SUMMARY BANNER ===== */
        .summary-banner {
            background: linear-gradient(135deg, rgba(102,126,234,0.15), rgba(118,75,162,0.15));
            border: 2px solid rgba(102,126,234,0.3);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            margin-bottom: 30px;
        }
        .summary-content {
            font-size: 1.2em; font-weight: 700; color: var(--text); margin-bottom: 15px;
        }
        .summary-content .highlight { color: var(--gold); font-size: 1.4em; }
        .btn-draw {
            background: linear-gradient(135deg, #11998e, #38ef7d); border: none; border-radius: 8px; padding: 12px 24px; font-size: 1.1em;
            font-weight: 800; color: white; cursor: pointer; transition: all 0.3s; box-shadow: 0 4px 15px rgba(17,153,142,0.4); font-family: 'Sarabun', sans-serif;
        }
        .btn-draw:hover { transform: translateY(-3px); box-shadow: 0 6px 20px rgba(17,153,142,0.6); }

        .flash { animation: flashGold 0.8s ease-out; }
    </style>"""
text = text.replace(css_old, css_new)

# 2. HTML
html_old = """    <!-- PODIUM -->"""
html_new = """    <!-- SUMMARY BANNER -->
    <div class="summary-banner" id="summaryBanner" style="display:none;">
        <div class="summary-content" id="summaryContent"></div>
        <button id="btnTieBreaker" class="btn-draw" style="display:none;">🎲 จับฉลากสุ่มหาผู้ชนะ</button>
    </div>

    <!-- PODIUM -->"""
text = text.replace(html_old, html_new)

html_old2 = """</div>

<script type="module">"""
html_new2 = """    <!-- DRAW MODAL -->
    <div class="modal" id="drawModal">
        <div class="modal-box">
            <h2 style="margin-top:0;">🎲 สุ่มผู้ชนะ (คะแนนเสมอกัน)</h2>
            <div id="drawAnimation" style="font-size: 3em; padding: 40px 0; font-weight: bold;">?</div>
            <div id="drawResult" style="display:none; margin-bottom: 20px;"></div>
            <button class="back-btn" id="btnCloseDraw" style="margin: 0 auto; display:none; background:rgba(255,255,255,0.1); color:#fff;" onclick="document.getElementById('drawModal').classList.remove('show')">ปิดหน้าต่าง</button>
        </div>
    </div>
</div>

<script type="module">"""
text = text.replace(html_old2, html_new2)

# 3. Imports
imp_old = """    import { getFirestore, collection, getDocs, onSnapshot, query, orderBy, doc }
        from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js';"""
imp_new = """    import { getFirestore, collection, getDocs, onSnapshot, query, orderBy, doc, setDoc }
        from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js';"""
text = text.replace(imp_old, imp_new)

# 4. Shared state & functions
state_old = """    // ===== SHARED STATE =====
    let latestVotes      = [];   // array of { name, votes }
    let latestClassrooms = [];

    // ===== LISTEN PARTY NAMES CONFIG =====
    onSnapshot(doc(db, 'config', 'partyDetails'), (docSnap) => {
        if (docSnap.exists() && docSnap.data().parties) {
            partyConfig = docSnap.data().parties;
            if (latestVotes.length > 0) {
                const total = latestVotes.reduce((s, p) => s + p.votes, 0);
                renderPodium(latestVotes, total);
                renderTable(latestVotes, total);
            }
        }
    });

    // ===== LISTEN VOTES (real-time) =====
    onSnapshot(collection(db, 'votes'), (snapshot) => {
        // Tally votes per party
        const tally = {};
        snapshot.forEach(docSnap => {
            const party = docSnap.data().party;
            if (party) tally[party] = (tally[party] || 0) + 1;
        });

        // Include all known parties even if 0 votes
        Object.keys(partyConfig).forEach(p => {
            if (!(p in tally)) tally[p] = 0;
        });

        latestVotes = Object.entries(tally)
            .map(([name, votes]) => ({ name, votes }))
            .sort((a, b) => b.votes - a.votes || a.name.localeCompare(b.name, 'th'));

        const total = latestVotes.reduce((s, p) => s + p.votes, 0);
        renderPodium(latestVotes, total);
        renderTable(latestVotes, total);
        renderStats(latestVotes, latestClassrooms);
    }, (err) => {
        console.error('votes snapshot error:', err);
        document.getElementById('lastUpdate').textContent = '⚠️ ไม่สามารถเชื่อมต่อ Firebase ได้';
    });"""

state_new = """    // ===== SHARED STATE =====
    let latestVotes      = [];   
    let latestClassrooms = [];
    let globalTally      = {};
    let forcedWinner     = null;
    let forcedWinnerVotes= 0;

    function processAndRender() {
        let arr = Object.entries(globalTally).map(([name, votes]) => ({ name, votes }));
        Object.keys(partyConfig).forEach(p => {
            if (!arr.find(x => x.name === p)) arr.push({ name: p, votes: 0 });
        });
        
        arr.sort((a, b) => {
            if (b.votes !== a.votes) return b.votes - a.votes;
            if (forcedWinner && forcedWinnerVotes === a.votes) {
                if (a.name === forcedWinner) return -1;
                if (b.name === forcedWinner) return 1;
            }
            return (partyConfig[a.name]?.name || a.name).localeCompare(partyConfig[b.name]?.name || b.name, 'th');
        });
        latestVotes = arr;

        const total = latestVotes.reduce((s, p) => s + p.votes, 0);
        renderPodium(latestVotes, total);
        renderTable(latestVotes, total);
        renderStats(latestVotes, latestClassrooms);
        updateSummary();
    }

    function updateSummary() {
        const wrap = document.getElementById('summaryBanner');
        const content = document.getElementById('summaryContent');
        const btn = document.getElementById('btnTieBreaker');
        
        if (latestVotes.length === 0 || latestVotes[0].votes === 0) {
            wrap.style.display = 'none';
            return;
        }

        wrap.style.display = 'block';
        const topVotes = latestVotes[0].votes;
        const mathematicalTie = latestVotes.filter(p => p.votes === topVotes);

        if (mathematicalTie.length > 1) {
            if (forcedWinner && forcedWinnerVotes === topVotes && mathematicalTie.find(p => p.name === forcedWinner)) {
                let winnerName = (partyConfig[forcedWinner] || {}).name || forcedWinner;
                content.innerHTML = `🏁 ผู้ชนะจากการจับฉลากคือ <span class="highlight">${winnerName}</span> (คะแนน ${topVotes} เสียง)`;
                btn.style.display = 'none';
            } else {
                let names = mathematicalTie.map(p => (partyConfig[p.name] || {}).name || p.name).join(' และ ');
                content.innerHTML = `⚠️ ขณะนี้มีคะแนนนำเสมอกันที่ <span class="highlight">${topVotes}</span> เสียง ระหว่าง ${names}`;
                btn.style.display = 'inline-block';
                btn.onclick = () => window.openDrawModal(mathematicalTie, topVotes);
            }
        } else {
            let winnerName = (partyConfig[latestVotes[0].name] || {}).name || latestVotes[0].name;
            content.innerHTML = `🏆 ขณะนี้อันดับ 1 คือ <span class="highlight">${winnerName}</span> ด้วยคะแนน ${topVotes} เสียง`;
            btn.style.display = 'none';
        }
    }

    window.openDrawModal = function(tiedParties, topVotes) {
        document.getElementById('drawModal').classList.add('show');
        const animBox = document.getElementById('drawAnimation');
        const resBox = document.getElementById('drawResult');
        const btnClose = document.getElementById('btnCloseDraw');
        
        animBox.style.display = 'block'; resBox.style.display = 'none'; btnClose.style.display = 'none';
        
        let counter = 0;
        let interval = setInterval(() => {
            let pName = tiedParties[counter % tiedParties.length].name;
            let p = partyConfig[pName] || { name: pName, color: '#fff' };
            animBox.innerHTML = `<span style="color:${p.color}">${p.name}</span>`;
            counter++;
        }, 100);
        
        setTimeout(async () => {
            clearInterval(interval);
            let winner = tiedParties[Math.floor(Math.random() * tiedParties.length)];
            let p = partyConfig[winner.name] || { name: winner.name, color: '#fff' };
            animBox.style.display = 'none';
            resBox.style.display = 'block';
            resBox.innerHTML = `ผู้ชนะคือ <br><span style="color:${p.color}; font-size:1.4em">${p.name}</span> ✨`;
            btnClose.style.display = 'inline-block';
            
            try {
                await setDoc(doc(db, 'config', 'tieBreaker'), { winnerId: winner.name, votes: topVotes });
            } catch(e) { console.error("Save tieBreaker failed", e); }
        }, 3000);
    }

    // ===== LISTENERS =====
    onSnapshot(doc(db, 'config', 'partyDetails'), (docSnap) => {
        if (docSnap.exists() && docSnap.data().parties) {
            partyConfig = docSnap.data().parties;
            processAndRender();
        }
    });

    onSnapshot(doc(db, 'config', 'tieBreaker'), (docSnap) => {
        if (docSnap.exists()) {
            forcedWinner = docSnap.data().winnerId;
            forcedWinnerVotes = docSnap.data().votes;
        } else {
            forcedWinner = null;
            forcedWinnerVotes = 0;
        }
        processAndRender();
    });

    onSnapshot(collection(db, 'votes'), (snapshot) => {
        globalTally = {};
        snapshot.forEach(docSnap => {
            const party = docSnap.data().party;
            if (party) globalTally[party] = (globalTally[party] || 0) + 1;
        });
        processAndRender();
    }, (err) => {
        console.error('votes snapshot error:', err);
        document.getElementById('lastUpdate').textContent = '⚠️ ไม่สามารถเชื่อมต่อ Firebase ได้';
    });"""

text = text.replace(state_old, state_new)

with open("results.html", "w", encoding="utf-8") as f:
    f.write(text)
print("done")
