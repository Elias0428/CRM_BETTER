const idsSelectWithValidation = ['agent_usa', 'sex', 'migration_status','dateMedicare']



document.getElementById('formCreateClientMedicare').addEventListener('submit', function(event) {
    console.log(idsSelectWithValidation)
    event.preventDefault(); // Previene el envío por defecto del formulario
    let isValid = true;
    const phoneNumber = document.getElementById('phone_number')

    date_birth = document.getElementById('date_birth')
    dateMedicare = document.getElementById('dateMedicare')

    if (date_birth.value == ''){
        isValid = false
        date_birth.focus()
    }

    if (dateMedicare.value == ''){
        isValid = false
        dateMedicare.focus()
    }

    // Función para validar los Select
    for (let i = 0; i < idsSelectWithValidation.length; i++) {
        var idSelect = idsSelectWithValidation[i];
        console.log(idSelect)
        var select = document.getElementById(idSelect);
        console.log(select)
        if (select.value == 'no_valid') {
            isValid = false;
            select.focus(); // Hace foco en el select inválido
            break; // Detiene la iteración
        }
    }

    phoneNumberFormat = validatePhoneNumber(phoneNumber.value)

    if (!isValid){
        return;
    }else if(phoneNumberFormat == false) {
        phoneNumber.focus()
        return;
    }
    phoneNumber.value = phoneNumberFormat
    //console.log('Papi llego hasta aqui. lo mando mi loco')
    this.submit();
});


function validatePhoneNumber(phoneNumber) {
    // Eliminar cualquier caracter que no sea número
    const cleanNumber = phoneNumber.toString().replace(/\D/g, '');
    
    // Si el número empieza con 1 y tiene 11 dígitos, es válido
    if (cleanNumber.startsWith('1') && cleanNumber.length === 11) {
        return cleanNumber;
    }
    
    // Si el número tiene exactamente 10 dígitos, agregar 1 al inicio
    if (cleanNumber.length === 10) {
        return '1' + cleanNumber;
    }
    
    // En cualquier otro caso, el número no es válido
    return false;
}

document.getElementById('zipcode').addEventListener('input', function() {
    const zipcode = this.value.trim(); // Elimina espacios en blanco

    if (zipcode.length === 5) { // Solo buscar cuando tenga 5 dígitos
        // 1️⃣ Consultar Zippopotam para obtener ciudad, estado y coordenadas
        fetch(`https://api.zippopotam.us/us/${zipcode}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error("ZIP Code no encontrado");
                }
                return response.json();
            })
            .then(data => {
                const city = data.places[0]['place name'];
                const state = data.places[0]['state abbreviation'];
                const lat = data.places[0]['latitude'];
                const lon = data.places[0]['longitude'];

                document.getElementById('city').value = city;
                document.getElementById('state').value = state;

                // 2️⃣ Consultar OpenStreetMap para obtener el condado usando las coordenadas
                return fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}`);
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error("Error al obtener el condado");
                }
                return response.json();
            })
            .then(data => {
                const county = data.address.county || " ";
                document.getElementById('county').value = county;
            })
            .catch(error => {
                console.error('Error obteniendo datos:', error);
                limpiarCampos(); // Limpiar si hay error
            });
    } else {
        limpiarCampos(); // Limpiar cuando el usuario borra los números
    }
});

// Función para limpiar los campos
function limpiarCampos() {
    document.getElementById('city').value = "";
    document.getElementById('state').value = "";
    document.getElementById('county').value = "";
}

document.addEventListener('DOMContentLoaded', function () {

    flatpickr("#date_birth", {
        dateFormat: "m/d/Y", // Formato MM/DD/YYYY
    });

    const fechaActual = new Date();
    let fechaMinima = new Date(fechaActual.getTime() + 42 * 60 * 60 * 1000); // 72 horas después

    // Ajustar fecha mínima para que sea entre 8 AM y 8 PM
    if (fechaMinima.getHours() < 8) {
        fechaMinima.setHours(8, 0, 0, 0);
    } else if (fechaMinima.getHours() >= 20) {
        fechaMinima.setDate(fechaMinima.getDate() + 1);
        fechaMinima.setHours(8, 0, 0, 0);
    }

    const dateMedicareInput = document.getElementById("dateMedicare");

    flatpickr(dateMedicareInput, {
        enableTime: true,
        noCalendar: false,
        dateFormat: "m/d/Y H", // Formato con AM/PM sin minutos
        time_24hr: true, // Formato de 12 horas con AM/PM
        minDate: fechaMinima,
        defaultDate: fechaMinima,
        minTime: "08:00",
        maxTime: "20:00",
        minuteIncrement: 60, // Solo permite horas completas (8AM, 9AM, etc.)
        onClose: function (selectedDates, dateStr, instance) {
            if (selectedDates.length > 0) {
                let selectedDate = selectedDates[0];

                let selectedHour = selectedDate.getHours();

                // ⛔️ Si la hora está fuera del rango, mostrar SweetAlert y borrar la selección
                if (selectedHour < 8 || selectedHour >= 20) {
                    Swal.fire({
                        icon: "warning",
                        title: "Time not allowed",
                        text: "You can only select an appointment between 8 AM and 8 PM.",
                        confirmButtonText: "Understood"
                    });
                    instance.clear(); // Borrar la selección inválida
                    return; // Salir de la función para evitar continuar con la validación
                }

                let formattedDate = instance.formatDate(selectedDate, "Y-m-d H:00"); // Formato compatible con Django

                // Obtener el agente seleccionado
                let agentUSA = document.getElementById("agent_usa").value;

                // Validar que el usuario haya seleccionado un agente
                if (agentUSA === "no_valid") {
                    Swal.fire({
                        icon: "warning",
                        title: "Agent not selected",
                        text: "Please select an agent before choosing a time.",
                        confirmButtonText: "OK"
                    });
                    instance.clear();
                    return;
                }

                // Enviar la fecha y el agente a Django para validación
                fetch(`/validarCita/?fecha=${formattedDate}&agente=${encodeURIComponent(agentUSA)}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.ocupado) {
                            Swal.fire({
                                icon: "error",
                                title: "Busy hour",
                                text: `The agent ${agentUSA} already has an appointment at that date and time.`,
                                confirmButtonText: "Understood",
                                timer: 8000,
                                timerProgressBar: true
                            });
                            instance.clear();  // Borrar la fecha seleccionada si está ocupada
                        }
                    })
                    .catch(error => {
                        console.error("Error en la validación:", error);
                        Swal.fire({
                            icon: "error",
                            title: "Error",
                            text: "A problem occurred while validating the time. Please try again.",
                            confirmButtonText: "OK"
                        });
                    });
            }
        }
    });
});
