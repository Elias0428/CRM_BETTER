const userSocket = new WebSocket('ws://' + window.location.host + '/ws/user-update/');
	
userSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    if (data.status === 'success') {
        Swal.fire({
            title: "<p class='text-dark'>Congratulations </p>",
            text: "For your new plan sold",
            icon: "success",
            confirmButtonText: "YeaH!",
        }).then((result) => {
            location.reload();
            if (result.isConfirmed) {
                location.reload();
            }
        });
        // Esperar 30 segundos (30000 milisegundos) antes de recargar la página
        setTimeout(function() {
            location.reload();  // Recarga la página
        }, 30000);  // 30 segundos
    }
};

// Function to start a countdown and redirect after 14 minutes
function startRedirectTimer(redirectUrl) {
    // Ensure the DOM is fully loaded before starting the timer
    document.addEventListener('DOMContentLoaded', () => {
        // Set the duration in milliseconds (14 minutes = 14 * 60 * 1000)
        const duration = 14 * 60 * 1000;

        // Set a timeout to redirect after the specified duration
        setTimeout(() => {
            window.location.href = redirectUrl;
        }, duration);
    });
}