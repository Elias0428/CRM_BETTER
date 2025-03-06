
document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('drawingCanvas');
    const ctx = canvas.getContext('2d');
    const form = document.getElementById('signatureForm');
    const signatureInput = document.getElementById('signatureInput');
    const clearCanvasButton = document.getElementById('clearCanvas');

    let drawing = false;

    // Configurar el estilo del dibujo
    ctx.lineWidth = 5;
    ctx.lineCap = 'round';
    ctx.strokeStyle = '#000';

    const startDrawing = (event) => {
        drawing = true;
        ctx.beginPath();
        ctx.moveTo(getX(event), getY(event));
    };

    const draw = (event) => {
        if (!drawing) return;
        ctx.lineTo(getX(event), getY(event));
        ctx.stroke();
    };

    const stopDrawing = () => {
        drawing = false;
        ctx.closePath();
    };

    const getX = (event) => {
        const rect = canvas.getBoundingClientRect();
        return event.touches ? event.touches[0].clientX - rect.left : event.clientX - rect.left;
    };

    const getY = (event) => {
        const rect = canvas.getBoundingClientRect();
        return event.touches ? event.touches[0].clientY - rect.top : event.clientY - rect.top;
    };

    // Verificar si el canvas está vacío
    const isCanvasEmpty = () => {
        const pixels = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
        for (let i = 0; i < pixels.length; i += 4) {
            if (pixels[i + 3] !== 0) { // Comprueba si hay algún píxel no transparente
                return false;
            }
        }
        return true;
    };

    // Eventos de dibujo
    canvas.addEventListener('mousedown', startDrawing);
    canvas.addEventListener('mousemove', draw);
    canvas.addEventListener('mouseup', stopDrawing);
    canvas.addEventListener('mouseout', stopDrawing);
    canvas.addEventListener('touchstart', startDrawing);
    canvas.addEventListener('touchmove', draw);
    canvas.addEventListener('touchend', stopDrawing);
    canvas.addEventListener('touchcancel', stopDrawing);

    // Limpiar canvas
    clearCanvasButton.addEventListener('click', () => {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
    });

    // Antes de enviar el formulario, convierte el canvas a Base64
    form.addEventListener('submit', (event) => {
        event.preventDefault();
        if (isCanvasEmpty()) {
            canvas.focus()
            alert('{% trans "Por favor, firma antes de enviar el formulario." %}');
            return;
        }
        const canvasData = canvas.toDataURL('image/png'); // Base64 de la firma
        signatureInput.value = canvasData; // Pasa la firma al campo oculto
        if (!validateSelects()) {
            return;
        }
        form.submit()
    });
});




function validateSelects() {
    const idsSelectWithValidation = ['apply', 'work', 'migration_status', 'selectAgent']
    console.log(idsSelectWithValidation)
    let isValid = true;
    const phoneNumber = document.getElementById('phone_number')


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

    if (!isValid){
        return false;
    }
    return true;
}



const dropzone = document.getElementById("dropzone");
const fileInput = document.getElementById("fileInput");
const fileList = document.getElementById("fileList");

// Lista para almacenar los archivos acumulados
let uploadedFiles = [];

// Hacer clic en el área de arrastre para abrir el selector de archivos
dropzone.addEventListener("click", () => fileInput.click());

// Manejar la carga de archivos con el selector
fileInput.addEventListener("change", (event) => {
    const files = Array.from(event.target.files);
    handleFiles(files);
});

// Manejar el arrastre y suelta
dropzone.addEventListener("dragover", (event) => {
    event.preventDefault();
    dropzone.style.borderColor = "#fc792f";
});

dropzone.addEventListener("dragleave", () => {
    dropzone.style.borderColor = "#ddd";
});

dropzone.addEventListener("drop", (event) => {
    event.preventDefault();
    dropzone.style.borderColor = "#ddd";
    const files = Array.from(event.dataTransfer.files);
    handleFiles(files);
});

// Función para manejar los archivos
function handleFiles(files) {
    files.forEach((file) => {
        // Evitar duplicados
        if (!uploadedFiles.find((f) => f.name === file.name && f.size === file.size)) {
            uploadedFiles.push(file);
            addFileToList(file);
        }
    });
}

// Agregar archivo a la lista visual
function addFileToList(file) {
    const listItem = document.createElement("li");
    listItem.className = "list-group-item d-flex justify-content-between align-items-center";

    const fileInfo = document.createElement("div");
    fileInfo.innerHTML = `
        <i class="bi bi-file-earmark"></i>
        <span>${file.name}</span>
    `;

    const fileSize = document.createElement("span");
    fileSize.className = "text-muted small";
    fileSize.textContent = `${(file.size / 1024).toFixed(1)}KB`;

    const deleteButton = document.createElement("button");
    deleteButton.className = "btn btn-sm btn-outline-danger";
    deleteButton.innerHTML = '<i class="bi bi-trash"></i>';
    deleteButton.onclick = () => {
        // Eliminar archivo de la lista
        uploadedFiles = uploadedFiles.filter((f) => f !== file);
        fileList.removeChild(listItem);
    };

    listItem.appendChild(fileInfo);
    listItem.appendChild(fileSize);
    listItem.appendChild(deleteButton);
    fileList.appendChild(listItem);
}



// Obtener elementos del DOM
const inputName = document.getElementById('inputName');
const inputLastName = document.getElementById('inputLastName');
const selectAgent = document.getElementById('selectAgent');
const insuranceAgency = document.getElementById('insuranceAgency');

// Crear un array dinámicamente de los inputs
const inputs = [inputName, inputLastName];

// Agregar eventos de entrada a cada input
inputs.forEach(input => {
    input.addEventListener('input', updateSpan);
});

// Actualizar el span con los valores de los inputs
function updateSpan() {
    changeSpan('textName', `${inputName.value} ${inputLastName.value}`);
    changeSpan('textName2', `${inputName.value} ${inputLastName.value}`);
    changeSpan('textName3', `${inputName.value} ${inputLastName.value}`);
    changeSpan('textName4', `${inputName.value} ${inputLastName.value}`);
    changeSpan('textName5', `${inputName.value} ${inputLastName.value}`);
}

// Agregar evento al cambio del selectAgent
selectAgent.addEventListener('change', function () {
    // Obtener el texto del option seleccionado en lugar del value
    const selectedText = selectAgent.options[selectAgent.selectedIndex].text;
    changeSpan('textAgent', selectedText);
    changeSpan('textAgent2', selectedText);
    changeSpan('textAgent3', selectedText);
    changeSpan('textAgent4', selectedText);
    changeSpan('textAgent5', selectedText);

    updateCarrierByAgent(selectedText);
});



// Función para actualizar el contenido de un span
function changeSpan(id, text) {
    const span = document.getElementById(id);
    if (span) {
        span.innerText = text;
    }
}

// Función para actualizar los spans relacionados al carrier
function changeCarrierSpans(carrier) {
    changeSpan('textCarrier', carrier);
    changeSpan('textCarrier2', carrier);
    changeSpan('textCarrier3', carrier);
    changeSpan('textCarrier4', carrier);
    changeSpan('textCarrier5', carrier);
    changeSpan('textCarrier6', carrier);
    changeSpan('textCarrier7', carrier);
    changeSpan('textCarrier8', carrier);
    changeSpan('textCarrier9', carrier);
}

// Función para determinar y actualizar los spans del carrier según el agente
function updateCarrierByAgent(agent) {
    if (agent.includes('GINA') || agent.includes('LUIS')) {
        changeCarrierSpans('TRUINSURANCE GROUP LLC');
        insuranceAgency.value = 'TRUINSURANCE GROUP LLC'
    } else if (
        agent.includes('DANIEL') ||
        agent.includes('ZOHIRA') ||
        agent.includes('DANIESKA') ||
        agent.includes('VLADIMIR') ||
        agent.includes('FRANK')
    ) {
        changeCarrierSpans('LAPEIRA & ASSOCIATES LLC');
        insuranceAgency.value = 'LAPEIRA & ASSOCIATES LLC'
    } else if (
        agent.includes('BORJA') ||
        agent.includes('RODRIGO') ||
        agent.includes('EVELYN')
    ) {
        changeCarrierSpans('SECUREPLUS INSURANCE LLC');
        insuranceAgency.value = 'SECUREPLUS INSURANCE LLC'
    } else {
        changeCarrierSpans(''); // Default value if no match
    }
}


document.addEventListener("DOMContentLoaded", function () {
    const revisarButton = document.getElementById("revisar");
    const devolverButton = document.getElementById("devolver");
    const canvas = document.getElementById("drawingCanvas");
    const ctx = canvas.getContext("2d");

    function isCanvasEmpty() {
        const blank = document.createElement("canvas");
        blank.width = canvas.width;
        blank.height = canvas.height;
        return canvas.toDataURL() === blank.toDataURL();
    }

    function toggleFields() {
        const fields = document.querySelectorAll("#signatureForm .mb-3");

        fields.forEach(field => {
            if (field.hasAttribute("hidden")) {
                field.removeAttribute("hidden");
            } else {
                field.setAttribute("hidden", "true");
            }
        });
    }

    function focusFirstVisibleInput() {
        setTimeout(() => {
            const visibleInputs = document.querySelectorAll("#signatureForm .mb-3:not([hidden]) input, #signatureForm .mb-3:not([hidden]) textarea, #signatureForm .mb-3:not([hidden]) select");
            if (visibleInputs.length > 0) {
                visibleInputs[0].focus(); // Enfoca el primer campo visible
            }
        }, 200); // Pequeño retraso para asegurarse de que los cambios de visibilidad se apliquen
    }

    revisarButton.addEventListener("click", function (event) {
        event.preventDefault();

        if (isCanvasEmpty()) {
            alert("Debe firmar antes de revisar.");
            return;
        }else if (!validatePhoneNumber()){
            alert("Valide su numero de telefono.");
            return;
        }else if (!validateEmail()){
            alert("Valide su Email.");
            return;
        }

        toggleFields();
        focusFirstVisibleInput(); // Asegura que el primer input visible reciba el foco
    });

    devolverButton.addEventListener("click", function (event) {
        event.preventDefault();
        toggleFields();
        focusFirstVisibleInput(); // También aplica el autofoco cuando se devuelve el formulario
    });

    // Detección de firma en el canvas
    let drawing = false;

    canvas.addEventListener("mousedown", () => (drawing = true));
    canvas.addEventListener("mouseup", () => (drawing = false));
    canvas.addEventListener("mousemove", function (event) {
        if (!drawing) return;

        const rect = canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;

        ctx.fillStyle = "black";
        ctx.beginPath();
        ctx.arc(x, y, 1, 0, 2 * Math.PI);
        ctx.fill();
    });

    // Botón para limpiar la firma
    const clearButton = document.getElementById("clearCanvas");
    clearButton.addEventListener("click", function () {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
    });
});

/**
 * Función que escucha cambios en inputs basado en un array de IDs
 * @param {string[]} inputIds - Array con los IDs de los inputs a escuchar
 * @param {Function} callback - Función que se ejecutará cuando cambie algún input
 */
function listenToInputChanges(inputIds, callback) {
  // Validar parámetros
  if (!Array.isArray(inputIds)) {
    throw new Error("El primer parámetro debe ser un array de strings");
  }

  if (typeof callback !== "function") {
    throw new Error("El segundo parámetro debe ser una función callback");
  }

  // Objeto para almacenar los valores actuales
  const currentValues = {};

  // Función para manejar los cambios
  function handleChange(event) {
    const inputId = event.target.id;
    const newValue = event.target.value;

    // Actualizar el valor en nuestro registro
    currentValues[inputId] = newValue;

    // Ejecutar callback con el id, valor y todos los valores actuales
    callback({
      inputId,
      value: newValue,
      allValues: { ...currentValues },
    });
  }

  // Agregar listeners a cada input
  inputIds.forEach((id) => {
    const inputElement = document.getElementById(id);

    if (!inputElement) {
      console.warn(`Input con ID '${id}' no encontrado`);
      return;
    }

    // Guardar valor inicial
    currentValues[id] = inputElement.value;

    // Agregar event listener
    inputElement.addEventListener("input", handleChange);
  });

  // Retornar función para eliminar los listeners cuando ya no se necesiten
  return function removeListeners() {
    inputIds.forEach((id) => {
      const inputElement = document.getElementById(id);
      if (inputElement) {
        inputElement.removeEventListener("input", handleChange);
      }
    });
  };
}

const inputIdsToListen = ['inputName', 'inputLastName', 'inputPhone', 'inputEmail', 'inputAddress', 'inputCity', 'inputState' ,'inputZipcode', 'inputDateBirth', 'inputTaxes', 'work', 'migration_status', 'selectAgent', 'insuranceAgency'];

const cleanup = listenToInputChanges(inputIdsToListen, (data) => {
    if (['inputName', 'inputLastName'].includes(data.inputId)) {
        changeinputsValue(`inputNameHidden`, `${data.allValues.inputName} ${data.allValues.inputLastName}`)
    }else if (['inputAddress', 'inputApto', 'inputCity', 'inputState', 'inputZipcode'].includes(data.inputId)){
        changeinputsValue(`inputAddressHidden`, `${data.allValues.inputAddress} ${data.allValues.inputCity} ${data.allValues.inputState} ${data.allValues.inputZipcode}`)
    }else if(data.inputId == 'agent_usa'){
        changeinputsValue(`selectAgentHidden`, data.allValues.selectAgent)
        changeinputsValue(`insuranceAgencyHidden`, data.allValues.insuranceAgency)
    }else if(['Telefono', 'Sms', 'Email', 'Whatsapp'].includes(data.inputId)){

    }else{
        changeinputsValue(`${data.inputId}Hidden`, data.value)
    }
});

function changeinputsValue(id, text) {
    const input = document.getElementById(id)
    input.value = text 
}

// Funcion para validar el numero de telefono:
const phoneInput = document.getElementById('inputPhone');
const errorDisplay = document.getElementById('error');

// Función de validación
function validatePhoneNumber() {
    let value = phoneInput.value;
    // Filtrar solo números
    value = value.replace(/[^0-9]/g, '');
    // Limitar a 11 caracteres
    if (value.length > 11) {
        value = value.slice(0, 11);
    }
    phoneInput.value = value;
    errorDisplay.style.display = 'none'; // Esconder mensaje de error al cambiar input

    if (phoneInput === document.activeElement) {
        return null; // Evitar validación completa mientras se escribe
    }
    
    // Validar al perder el enfoque
    if (value.length === 10) {
        // Si tiene 10 dígitos, agregar '1' al inicio
        phoneInput.value = '1' + value;
        return true;
    } else if (value.length === 11 && value.startsWith('1')) {
        return true;
    } else {
        // Si la longitud es incorrecta o no empieza con '1', mostrar error
        errorDisplay.style.display = 'block';
        phoneInput.focus()
        return false;
    }
}

// Asignar la función a eventos de input y blur
phoneInput.addEventListener('input', validatePhoneNumber);
phoneInput.addEventListener('blur', validatePhoneNumber);

const emailInput = document.getElementById('inputEmail');
const errorDisplayEmail = document.getElementById('errorEmail');

// Función de validación de email
function validateEmail() {
    const value = emailInput.value;
    errorDisplayEmail.style.display = 'none'; // Esconder mensaje de error al cambiar input
    
    // Expresión regular para validar email
    const emailRegex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/;
    
    if (emailInput === document.activeElement) {
        return null; // Evitar validación completa mientras se escribe
    }

    // Validar email
    if (emailRegex.test(value)) {
        return true;
    } else {
        // Mostrar error si el correo es inválido
        errorDisplayEmail.style.display = 'block';
        emailInput.focus()
        return false;
    }
}

// Asignar la función a eventos de input y blur
emailInput.addEventListener('input', validateEmail);
emailInput.addEventListener('blur', validateEmail);