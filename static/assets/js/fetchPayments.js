function sendDataPayments() {
    form = document.getElementById('formUser')
    console.log(form)

    const formData = new FormData(form);  // Obtiene los datos del formulario

    fetch('/fetchCreateUser/', {
      method: 'POST',
      body: formData,
    })
    .then(response => response.json())  // Procesar la respuesta (si es JSON)
    .then(data => {
        if (data.success){
            Swal.fire({
                title: "Good job!",
                text: "User successfully saved!",
                icon: "success",
                confirmButtonText: "Save",
            }).then((result) => {
                if (result.isConfirmed) {
                    location.reload();
                }
            });
        }else{
            //console.log(data.errors);
            let messages = data.errors; // Obtenemos directamente el objeto de errores
                        
            let formattedMessage = "There seems to be some problems with the form:\n\n";

            for (const [field, errors] of Object.entries(messages)) {
                formattedMessage += `<li><strong>${capitalizeFirstLetter(field)}</strong>:`;
                errors.forEach(error => {
                    formattedMessage += `  ${error}</li>`;
                });
            }

            Swal.fire({
                icon: "error",
                title: "Oops...",
                html: formattedMessage,
            });
        }
    })
    // .catch(error => console.error('Error:', error));  // Manejo de errores
}

function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

function listenAllCheckInput() {
    let paymentsTable = document.getElementById('paymentsTable')
    let checkboxes = paymentsTable.querySelectorAll('input[type="checkbox"]');

    // Para cada checkbox, agregar un oyente de eventos que se dispare al cambiar el estado del checkbox
    checkboxes.forEach(function(checkbox) {
        checkbox.addEventListener('change', function(event) {            
            toggleUserStatus(checkbox)
        });
    });
}

function toggleUserStatus(checkbox) {
    const formData = new FormData();
    formData.append('obamaCare', obamacare_id);
    formData.append('month', checkbox.value);

    if (checkbox.checked) {

        fetch(`/fetchPaymentsMonth/`, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())  // Procesar la respuesta (si es JSON)
        .then(data => {
            //console.log(data.success)
            if (data.success){
                //console.log("User role:", data.role); // Debugging
                if (data.success && data.role != "Admin") {
                    checkbox.disabled = true;
                }
            }
        })
        .catch(error => console.error('Error:', error));  // Manejo de errores
    } else {
        // Si se desmarca el checkbox, eliminar el pago
        fetch(`/fetchPaymentsMonth/`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                obamaCare: obamacare_id,
                month: checkbox.value
            })
        })
        .then(response => response.json())  
        .then(data => {
            if (data.success) {
                console.log("Payment deleted successfully");
            } else {
                console.error("Error deleting payment:", data.message);
            }
        })
        .catch(error => console.error('Error:', error));
    }
}

document.addEventListener('DOMContentLoaded', listenAllCheckInput);