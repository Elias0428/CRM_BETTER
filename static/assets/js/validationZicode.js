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
