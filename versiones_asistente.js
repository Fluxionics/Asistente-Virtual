document.addEventListener('DOMContentLoaded', () => {
    // Array de datos de versiones del Asistente Fluxi
    // DEBES REEMPLAZAR LOS VALORES 'TU_LINK_DE_VERSION_X' con los enlaces de descarga reales.
    const oldVersions = [
        {
            titulo: "Asistente Fluxi - Versión de Lanzamiento Beta",
            version: "v1.0.0",
            link: "https://drive.google.com/uc?export=download&id=1EO0lZcSSGGOz2LJj-sSC9VDl_PZ4y8FL" 
        }
        //{
           // titulo: "Asistente Fluxi - Corrección de Bugs Iniciales",
          //  version: "v1.0.1",
           // link: "https://drive.google.com/uc?export=download&id=TU_LINK_DE_VERSION_1_0_1" 
      //  },
      //  {
          //  titulo: "Asistente Fluxi - Versión Beta Cerrada (Experimental)",
        //    version: "v0.9.5-beta",
      //      link: "https://drive.google.com/uc?export=download&id=TU_LINK_DE_VERSION_0_9_5" 
      //  }
        // Puedes agregar más versiones aquí copiando y pegando el objeto {}
    ];

    const container = document.getElementById('versions-container');

    // Función para renderizar las versiones en el HTML
    const renderVersions = () => {
        if (!container) return; 

        container.innerHTML = ''; // Limpiar el mensaje de "Cargando..."

        oldVersions.forEach(version => {
            // Crea el HTML para cada tarjeta de versión
            const versionCard = `
                <div class="bg-slate-900/80 p-5 rounded-xl border border-slate-800 flex flex-col md:flex-row justify-between items-center hover:border-cyan-500/50 hover:shadow-[0_0_15px_rgba(6,182,212,0.1)] transition-all duration-300">
                    
                    <div class="text-left mb-4 md:mb-0 md:mr-6">
                        <h3 class="text-xl font-semibold text-white">${version.titulo}</h3>
                        <p class="text-cyan-400 font-mono text-sm mt-1">Versión: ${version.version}</p>
                    </div>

                    <a href="${version.link}" target="_blank" class="inline-flex items-center px-6 py-2 rounded-md text-sm font-medium transition-all bg-cyan-500 text-black hover:bg-cyan-400 flex-shrink-0">
                        Descargar
                        <svg class="ml-2 w-4 h-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
                    </a>
                </div>
            `;
            container.innerHTML += versionCard;
        });
    };
    
    // Iniciar la renderización
    renderVersions();
});
