// ✅ Registrar el plugin de validación de tipo de archivo
FilePond.registerPlugin(FilePondPluginFileValidateType);

document.addEventListener("DOMContentLoaded", function () {
    const inputElement = document.getElementById("pdfUploader");
    const fileNamesContainer = document.getElementById("fileNamesContainer");
    const uploadButton = document.getElementById("loadDocument");

    if (inputElement) {
        const pond = FilePond.create(inputElement, {
            acceptedFileTypes: ['application/pdf'],
            allowMultiple: true,
            allowProcess: false, // 🚀 Evita la subida automática
        });

        // 🔥 Evento para agregar un input de nombre cuando se sube un archivo
        pond.on("addfile", (error, fileItem) => {
            if (!error) {
                const input = document.createElement("input");
                input.type = "text";
                input.placeholder = `Name for ${fileItem.filename}`;
                input.name = "filenames"; // ✅ Se almacena en una lista en el backend
                input.className = "form-control mt-2";
                input.dataset.fileId = fileItem.id;
                fileNamesContainer.appendChild(input);
            }
        });

        // ✅ Eliminar el campo de nombre cuando se borra un archivo
        pond.on("removefile", (error, fileItem) => {
            if (!error) {
                const input = document.querySelector(`input[data-file-id="${fileItem.id}"]`);
                if (input) {
                    input.remove();
                }
            }
        });

        // ✅ Evento para subir archivos cuando se presiona el botón
        uploadButton.addEventListener("click", async (event) => {
            event.preventDefault(); // ❌ Evita que el formulario se envíe automáticamente

            const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]")?.value || "";
            const formData = new FormData();

            // 🚀 Mostrar un mensaje de "Subiendo archivos..."
            Swal.fire({
                title: "Uploading files...",
                text: "Please wait a moment.",
                allowOutsideClick: false,
                didOpen: () => {
                    Swal.showLoading();
                }
            });

            // 🚀 Subir cada archivo con su nombre asociado
            for (const fileItem of pond.getFiles()) {
                formData.append("documents", fileItem.file);

                // Obtener el nombre del archivo ingresado
                const input = document.querySelector(`input[data-file-id="${fileItem.id}"]`);
                const fileName = input?.value.trim() || fileItem.filename; // ✅ Si no hay nombre, usa el del archivo
                formData.append("filenames", fileName);
            }

            // ✅ Enviar al backend
            fetch(uploadButton.dataset.uploadUrl, {  // ✅ La URL se pasa como atributo en el HTML
                method: "POST",
                headers: { "X-CSRFToken": csrfToken },
                body: formData
            })
            .then(response => response.json())
            .then(res => {
                if (res.success) {
                    Swal.fire({
                        title: "Success!",
                        text: res.message,
                        icon: "success",
                        confirmButtonText: "Continue"
                    }).then(() => {
                        window.location.href = res.redirect_url;
                    });
                } else {
                    Swal.fire("Error", res.message, "error");
                }
            })
            .catch(error => {
                console.error("Error:", error);
                Swal.fire("Error", "A problem occurred while uploading files", "error");
            });
        });

        pond.on("error", (error) => {
            console.error("Error en FilePond:", error);
        });
    } else {
        console.error("The element #pdfUploader was not found.");
    }
});
