
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
        form.submit()
    });
});











document.addEventListener("DOMContentLoaded", function () {
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



