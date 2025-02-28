// Scroll suave para enlaces internos
document.addEventListener('DOMContentLoaded', function() {
    // Seleccionar todos los enlaces con atributo data-scroll
    const scrollLinks = document.querySelectorAll('a[data-scroll]');
    
    scrollLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Prevenir el comportamiento predeterminado
            e.preventDefault();
            
            // Obtener el destino del enlace (sin el #)
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                // Calcular la posición de desplazamiento
                const offsetTop = targetElement.offsetTop;
                
                // Desplazar suavemente
                window.scrollTo({
                    top: offsetTop - 80, // Ajuste para el encabezado fijo
                    behavior: 'smooth'
                });
            }
        });
    });
});