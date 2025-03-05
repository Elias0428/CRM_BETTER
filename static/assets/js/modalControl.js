const modalVerTexto = document.getElementById('modalVerTexto');
modalVerTexto.addEventListener('show.bs.modal', function (event) {
    const button = event.relatedTarget; // Botón que abrió el modal
    const agent = button.getAttribute('data-bs-agent');
    const agent_create = button.getAttribute('data-bs-agent-create');
    const category = button.getAttribute('data-bs-category');
    const amount = button.getAttribute('data-bs-amount');
    const date = button.getAttribute('data-bs-date');
    const findings = button.getAttribute('data-bs-findings');
    const observation = button.getAttribute('data-bs-observation');

    // Actualizar el contenido del modal
    modalVerTexto.querySelector('#modal-agent').textContent = agent;
    modalVerTexto.querySelector('#modal-agent-create').textContent = agent_create;
    modalVerTexto.querySelector('#modal-date').textContent = date;
    modalVerTexto.querySelector('#modal-category').textContent = category;
    modalVerTexto.querySelector('#modal-amount').textContent = amount;			
    modalVerTexto.querySelector('#modal-findings').textContent = findings;
    modalVerTexto.querySelector('#modal-observation').textContent = observation;
});

const modalViewCall = document.getElementById('modalViewCall');
modalViewCall.addEventListener('show.bs.modal', function (event) {
    const button = event.relatedTarget; // Botón que abrió el modal
    const agent_call = button.getAttribute('data-bs-call-agent');
    const agent_create_call = button.getAttribute('data-bs-call-agent-create');
    const date_call = button.getAttribute('data-bs-call-date');
    const daily_call = button.getAttribute('data-bs-call-daily');
    const answered_call = button.getAttribute('data-bs-call-answered');			
    const mins_call = button.getAttribute('data-bs-call-mins');

    // Actualizar el contenido del modal
    modalViewCall.querySelector('#modal-call-agent').textContent = agent_call;
    modalViewCall.querySelector('#modal-agent-call-create').textContent = agent_create_call;
    modalViewCall.querySelector('#modal-call-date').textContent = date_call;
    modalViewCall.querySelector('#modal-call-daily').textContent = daily_call;
    modalViewCall.querySelector('#modal-call-answered').textContent = answered_call;			
    modalViewCall.querySelector('#modal-call-mins').textContent = mins_call;
    modalViewCall.querySelector('#modal-call-observation').textContent = observation_call;
});