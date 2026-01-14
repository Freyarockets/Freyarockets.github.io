/**
 * FREYA ROCKET SYSTEMS - Operations Engine 2026
 * Handles Token Sales, 3D Manufacturing, and Facility Construction
 */

const FreyaEngine = {
    state: {
        tokens: 0,
        parts: 0,
        facilities: 0,
        isPrinting: false
    },

    init: function() {
        console.log("Freya Operations System Active...");
        this.loadProgress();
        this.injectInterface();
        this.setupHooks();
    },

    // --- BLOCKCHAIN SIMULATION ---
    async buyTokens() {
        if (typeof window.ethereum !== 'undefined') {
            try {
                // Trigger existing GTM tracking
                if (typeof trackTokenBuy === 'function') trackTokenBuy();
                
                alert("Connecting to Ethereum Mainnet... \nRate: 1 ETH = 1000 FREYA Tokens");
                
                // Transaction logic would go here
                this.state.tokens += 100;
                this.saveProgress();
                this.updateUI();
            } catch (err) {
                console.error("Wallet connection failed", err);
            }
        } else {
            alert("MetaMask not detected. Please install the extension to buy tokens.");
        }
    },

    // --- MANUFACTURING ---
    printPart: function() {
        if (this.state.tokens < 10) {
            alert("Insufficient Tokens! You need 10 FREYA tokens to 3D print a component.");
            return;
        }

        if (this.state.isPrinting) return;

        this.state.isPrinting = true;
        this.state.tokens -= 10;
        this.updateUI();

        // Simulate 3D Printing Process
        setTimeout(() => {
            this.state.parts += 1;
            this.state.isPrinting = false;
            this.saveProgress();
            this.updateUI();
            alert("3D Print Complete: Rocket Engine Component added to inventory.");
        }, 4000);
    },

    // --- CONSTRUCTION ---
    buildFacility: function() {
        if (this.state.parts < 5) {
            alert("Resource Shortage: 5 3D-printed parts required to build a Launch Facility.");
            return;
        }

        this.state.parts -= 5;
        this.state.facilities += 1;
        this.saveProgress();
        this.updateUI();
        alert("Success: New Rocket Assembly Facility is now operational.");
    },

    // --- PERSISTENCE & UI ---
    saveProgress: function() {
        localStorage.setItem('freya_data', JSON.stringify(this.state));
    },

    loadProgress: function() {
        const saved = localStorage.getItem('freya_data');
        if (saved) this.state = JSON.parse(saved);
    },

    injectInterface: function() {
        const dashboard = document.createElement('div');
        dashboard.id = 'freya-dashboard';
        dashboard.style = `
            position: fixed; bottom: 20px; right: 20px; 
            background: rgba(0,0,0,0.9); color: #fff; 
            padding: 20px; border-radius: 10px; 
            border: 1px solid #3498db; z-index: 10000;
            font-family: sans-serif; box-shadow: 0 0 15px rgba(52,152,219,0.5);
        `;
        document.body.appendChild(dashboard);
        this.updateUI();
    },

    updateUI: function() {
        const db = document.getElementById('freya-dashboard');
        db.innerHTML = `
            <h6 style="margin-top:0; color:#3498db;">FREYA COMMAND CENTER</h6>
            <p style="margin:5px 0;">Tokens: <b>${this.state.tokens}</b></p>
            <p style="margin:5px 0;">Parts: <b>${this.state.parts}</b></p>
            <p style="margin:5px 0;">Facilities: <b>${this.state.facilities}</b></p>
            <hr style="border:0; border-top:1px solid #333;">
            <button onclick="FreyaEngine.printPart()" style="width:100%; margin-bottom:5px; cursor:pointer;" ${this.state.isPrinting ? 'disabled' : ''}>
                ${this.state.isPrinting ? 'PRINTING...' : '3D PRINT PART (-10 Tkn)'}
            </button>
            <button onclick="FreyaEngine.buildFacility()" style="width:100%; cursor:pointer;">BUILD FACILITY (-5 Parts)</button>
        `;
    },

    setupHooks: function() {
        // Automatically attach to the specific "BUY/OFFERS" link in your HTML
        const buyLink = document.querySelector('a[href="BuyFreyaToken.html"]');
        if (buyLink) {
            buyLink.addEventListener('click', (e) => {
                e.preventDefault();
                this.buyTokens();
            });
        }
    }
};

// Auto-start on page load
window.addEventListener('DOMContentLoaded', () => FreyaEngine.init());
