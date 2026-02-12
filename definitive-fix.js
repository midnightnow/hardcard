// DEFINITIVE FIX - This WILL work
console.log('🎯 DEFINITIVE FIX LOADING...');

// Wait for full page load
window.addEventListener('load', () => {
    console.log('🔧 Page loaded, applying definitive fix...');
    
    // First, let's make dashboard start hidden
    const dashboard = document.getElementById('dashboard-section');
    if (dashboard && !dashboard.classList.contains('hidden')) {
        console.log('⚠️ Dashboard was not hidden! Fixing...');
        dashboard.classList.add('hidden');
        dashboard.style.display = 'none';
    }
    
    // Create our own section switcher
    window.definitiveSwitcher = function(sectionName) {
        console.log(`🎯 DEFINITIVE: Switching to ${sectionName}`);
        
        // Get all sections
        const allSections = document.querySelectorAll('.content-section');
        
        // Hide EVERYTHING first
        allSections.forEach(section => {
            section.classList.add('hidden');
            section.setAttribute('style', 'display: none !important; visibility: hidden !important; opacity: 0 !important; position: absolute !important; left: -9999px !important; z-index: -1000 !important;');
        });
        
        // Show ONLY the target
        const target = document.getElementById(`${sectionName}-section`);
        if (target) {
            target.classList.remove('hidden');
            target.setAttribute('style', 'display: block !important; visibility: visible !important; opacity: 1 !important; position: relative !important; left: 0 !important; z-index: 10 !important;');
            
            console.log(`✅ ${sectionName} is now the ONLY visible section`);
            
            // Verify
            setTimeout(() => {
                const stillVisible = [];
                allSections.forEach(s => {
                    const style = window.getComputedStyle(s);
                    if (style.display !== 'none' && style.visibility !== 'hidden') {
                        stillVisible.push(s.id);
                    }
                });
                console.log('Visible sections after switch:', stillVisible);
            }, 100);
        }
    };
    
    // Override ALL navigation
    setTimeout(() => {
        // Replace showSection
        if (window.app && window.app.showSection) {
            const original = window.app.showSection;
            window.app.showSection = function(sectionName) {
                console.log(`🔄 Intercepted showSection(${sectionName})`);
                window.definitiveSwitcher(sectionName);
                
                // Still call original for UI updates
                if (window.app.updateActiveStates) {
                    window.app.updateActiveStates(sectionName);
                }
                if (window.app.showNotification) {
                    window.app.showNotification(`Switched to ${sectionName}`, 'info');
                }
            };
        }
        
        // Intercept ALL clicks
        document.body.addEventListener('click', (e) => {
            const btn = e.target.closest('[data-section]');
            if (btn) {
                e.preventDefault();
                e.stopPropagation();
                const section = btn.getAttribute('data-section');
                console.log(`🖱️ Click intercepted: ${section}`);
                window.definitiveSwitcher(section);
                
                // Update UI
                if (window.app && window.app.updateActiveStates) {
                    window.app.updateActiveStates(section);
                }
                return false;
            }
        }, true);
        
        // Show dashboard initially
        window.definitiveSwitcher('dashboard');
        
        console.log('✅ DEFINITIVE FIX FULLY APPLIED!');
    }, 500);
});