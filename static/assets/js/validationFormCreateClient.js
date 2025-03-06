const idsSelectWithValidation = ['agent_usa', 'sex', 'migration_status', 'type_sales', 'applyObama']



document.getElementById('formCreateClient').addEventListener('submit', function(event) {
    //console.log(idsSelectWithValidation)
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
        //console.log(idSelect)
        var select = document.getElementById(idSelect);
        //console.log(select)
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


