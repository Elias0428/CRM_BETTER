document.addEventListener('DOMContentLoaded', function() {
    // Selecciona todos los botones de vista
    const viewButtons = document.querySelectorAll('.view-observation');
    
    // Modal y sus elementos
    const modal = document.getElementById('observationDetailModal');
    const modalAgentName = document.getElementById('modal-agent-name');
    const modalClientName = document.getElementById('modal-client-name');
    const modalTypePolice = document.getElementById('modal-type-police');
    const modalTypeCall = document.getElementById('modal-type-call');
    const modalCreatedAt = document.getElementById('modal-created-at');
    const modalTypification = document.getElementById('modal-typification');
    const modalContent = document.getElementById('modal-content');

    // Añadir evento a cada botón
    viewButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const observationId = this.dataset.id;

            // Usar Fetch para obtener los datos
            fetch(`/get-observation-detail/${observationId}/`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Error en la respuesta');
                    }
                    return response.json();
                })
                .then(data => {
                    // Llenar los campos del modal
                    modalAgentName.textContent = data.agent_name;
                    modalClientName.textContent = data.client_name;
                    modalTypePolice.textContent = data.type_police;
                    modalTypeCall.textContent = data.type_call;
                    modalCreatedAt.textContent = data.created_at;
                    modalTypification.textContent = data.typification;
                    modalContent.textContent = data.content;

                    // Mostrar el modal (asumiendo que estás usando Bootstrap)
                    $(modal).modal('show');
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('No se pudieron cargar los detalles del registro');
                });
        });
    });
});