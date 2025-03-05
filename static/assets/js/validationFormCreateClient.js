const idsSelectWithValidation = ['agent_usa', 'sex', 'migration_status', 'type_sales', 'applyObama']



document.getElementById('formCreateClient').addEventListener('submit', function(event) {
    console.log(idsSelectWithValidation)
    event.preventDefault(); // Previene el envío por defecto del formulario
    let isValid = true;
    const phoneNumber = document.getElementById('phone_number')

    date_birth = document.getElementById('date_birth')

    if (date_birth.value == ''){
        isValid = false
        date_birth.focus()
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

