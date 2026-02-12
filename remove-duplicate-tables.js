// Remove duplicate client tables
console.log('🧹 Removing duplicate client tables...');

window.addEventListener('load', () => {
    setTimeout(() => {
        // Find all tables containing Sarah Johnson
        const allTables = document.querySelectorAll('table');
        const clientTables = [];
        
        allTables.forEach(table => {
            if (table.textContent.includes('Sarah Johnson') && table.textContent.includes('sarah.johnson@email.com')) {
                clientTables.push(table);
            }
        });
        
        console.log(`Found ${clientTables.length} client tables`);
        
        // Keep only the one in clients-section
        clientTables.forEach(table => {
            const section = table.closest('.content-section');
            if (section && section.id !== 'clients-section') {
                console.log(`⚠️ Removing client table from ${section.id}`);
                table.remove();
            }
        });
        
        // Also remove any orphan tables
        clientTables.forEach(table => {
            const section = table.closest('.content-section');
            if (!section) {
                console.log('⚠️ Removing orphan client table');
                table.remove();
            }
        });
        
        console.log('✅ Duplicate table cleanup complete');
    }, 1000);
});