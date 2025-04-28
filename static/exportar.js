// Efectos para tarjetas de exportación
document.addEventListener('DOMContentLoaded', function() {
    const cards = document.querySelectorAll('.card.h-100');
    
    cards.forEach(card => {
        // Efecto hover
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.transition = 'transform 0.3s ease';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = '';
        });
        
        // Efecto click
        card.addEventListener('mousedown', function() {
            this.style.transform = 'translateY(2px)';
        });
        
        card.addEventListener('mouseup', function() {
            this.style.transform = 'translateY(-5px)';
        });
    });
});