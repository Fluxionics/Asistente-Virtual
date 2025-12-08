document.addEventListener('DOMContentLoaded', () => {
    const oldVersions = [
       
        {
            titulo: "Asistente Fluxi - Primera Edición (Errores Críticos)",
            version: "v1.0.0",
            link: "https://drive.google.com/uc?export=download&id=1EO0lZcSSGGOz2LJj-sSC9VDl_PZ4y8FL", 
            descripcionCorta: "Cierres Comunes sin corrección de texto.",
            descripcionLarga: "Al Abrir La Configuración Y Cerrarla Se Craseaba. Errores de generación de texto. Letras Comidas (Unicode). API Key Invalida no era detectada correctamente." 
        },
        {
            titulo: "Asistente Fluxi - Corrección de Bugs Iniciales",
            version: "v1.0.1",
            link:  "https//:drive.google.com/uc?export=download&id=1EO0lZcSSGGOz2LJj-sSC9VDl_PZ4y8FL",
            descripcionCorta: "corrección de un bug en el comando de desbloqueo.",
            descripcionLarga: "Error De Claves, Nueva Funcion Ingconito, Configuraciones Nuevas Agregar Comandos Escritura." 
        }
    ];

    const container = document.getElementById('versions-container');
    const modal = document.getElementById('version-modal');
    const modalTitle = document.getElementById('modal-title');
    const modalVersion = document.getElementById('modal-version');
    const modalBody = document.getElementById('modal-body');
    const modalDownloadLink = document.getElementById('modal-download-link');
    const closeButton = document.getElementById('close-modal');

    // Función para renderizar las versiones en el HTML
    const renderVersions = () => {
        if (!container) return; 

        container.innerHTML = ''; 

        oldVersions.forEach((version, index) => {
            // Se usa el índice como ID para el modal
            const versionCard = `
                <div class="bg-slate-900/80 p-5 rounded-xl border border-slate-800 flex flex-col md:flex-row justify-between items-center hover:border-cyan-500/50 hover:shadow-[0_0_15px_rgba(6,182,212,0.1)] transition-all duration-300">
                    
                    <div class="text-left mb-4 md:mb-0 md:mr-6 flex-grow">
                        <h3 class="text-xl font-semibold text-white">${version.titulo} <span class="text-cyan-400 font-mono text-base ml-2">(${version.version})</span></h3>
                        <p class="text-slate-400 text-sm mt-1">${version.descripcionCorta}</p>
                    </div>

                    <div class="flex flex-col sm:flex-row gap-3 flex-shrink-0">
                        <button data-index="${index}" class="open-modal-btn inline-flex items-center px-4 py-2 rounded-md text-sm font-medium transition-all bg-slate-700 text-white hover:bg-slate-600 flex-shrink-0">
                            Ver Cambios
                        </button>
                        
                        <a href="${version.link}" target="_blank" class="inline-flex items-center px-4 py-2 rounded-md text-sm font-medium transition-all bg-cyan-500 text-black hover:bg-cyan-400 flex-shrink-0">
                            Descargar
                            <svg class="ml-2 w-4 h-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
                        </a>
                    </div>
                </div>
            `;
            container.innerHTML += versionCard;
        });

        // Asignar eventos a los botones después de que el HTML esté en el DOM
        document.querySelectorAll('.open-modal-btn').forEach(button => {
            button.addEventListener('click', (e) => {
                const index = e.target.getAttribute('data-index');
                const selectedVersion = oldVersions[index];
                
                // Llenar el modal
                modalTitle.textContent = selectedVersion.titulo;
                modalVersion.textContent = `(${selectedVersion.version})`;
                // Usar innerHTML y replace para que el texto largo se muestre correctamente
                modalBody.innerHTML = selectedVersion.descripcionLarga.replace(/\n/g, '<br>');
                modalDownloadLink.href = selectedVersion.link;
                
                // Mostrar el modal
                modal.classList.remove('hidden');
                modal.classList.add('flex');
            });
        });
    };
    
    // Cerrar el modal
    closeButton.addEventListener('click', () => {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
    });

    // Cerrar el modal al hacer clic fuera de él
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.add('hidden');
            modal.classList.remove('flex');
        }
    });

    renderVersions();
});
