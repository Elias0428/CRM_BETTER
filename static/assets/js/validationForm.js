document.addEventListener("DOMContentLoaded", function() {
    const buttonNext = document.getElementById('buttonSendSupp');
    const supplementaryContainer = document.getElementById('supplementary-container');
  
    // Función para obtener todos los campos requeridos
    function getRequiredInputs() {
      return supplementaryContainer.querySelectorAll('input[required], select[required], textarea[required]');
    }
  
    // Función de validación
    function validateForm() {
      const inputs = getRequiredInputs(); // Obtener todos los campos requeridos
      let isValid = true;
  
      inputs.forEach(input => {
        if (!input.checkValidity()) {
          isValid = false; // Si alguna entrada no es válida, deshabilitar el botón
        }
      });
  
      // Habilitar o deshabilitar el botón "Next"
      buttonNext.disabled = !isValid;
    }
  
    // Validar cuando el valor de los campos cambie
    supplementaryContainer.addEventListener('input', function(event) {
      if (event.target.matches('input[required], select[required], textarea[required]')) {
        validateForm();
      }
    });
  
    // Validar al cargar la página para establecer el estado inicial del botón
    validateForm();
  });