// Función para manejar el cierre de sesión
function setupSessionTimeout() {
    
    // Configuraciones de tiempo
    const TIMEOUT_DURATION = 15 * 60 * 1000; // 15 minutos
    const WARNING_TIME = 2 * 60 * 1000; // 2 minutos antes del cierre
    const AUTO_LOGOUT_AFTER_WARNING = 1 * 60 * 1000; // 1 minuto después de la alerta

    let timeoutId;
    let warningTimeoutId;
    let autoLogoutTimeoutId;

    // Función para cerrar sesión
    function performLogout() {
        
        try {
            fetch('/logout/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin'
            })
            .then(response => {
                return response.json();
            })
            .then(data => {
                
                // Asegurarse de redirigir
                if (data.redirect_url) {
                    window.location.href = data.redirect_url;
                } else {
                    window.location.href = '/login/';
                }
            })
            .catch(error => {
                window.location.href = '/login/';
            });
        } catch (error) {
            window.location.href = '/login/';
        }
    }

    // Función para mostrar advertencia
    function showWarning() {
        
        // Mostrar confirmación
        const confirmed = confirm('Su sesión está a punto de expirar. Si no responde, se cerrará automáticamente en 1 minuto. ¿Desea continuar?');

        if (confirmed) {
            performLogout(); // Cierra la sesión directamente si el usuario confirma
        } else {
            autoLogoutTimeoutId = setTimeout(() => {
                performLogout();
            }, AUTO_LOGOUT_AFTER_WARNING);
        }
    }

    // Función para reiniciar temporizadores
    function resetTimer() {
        
        // Limpiar temporizadores anteriores
        clearTimeout(timeoutId);
        clearTimeout(warningTimeoutId);
        clearTimeout(autoLogoutTimeoutId);

        // Configurar nuevos temporizadores
        timeoutId = setTimeout(performLogout, TIMEOUT_DURATION);
        warningTimeoutId = setTimeout(showWarning, TIMEOUT_DURATION - WARNING_TIME);
    }

    // Función para obtener cookie CSRF
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Eventos para reiniciar el temporizador
    const resetEvents = [
        'mousedown', 
        'keydown', 
        'scroll', 
        'mousemove', 
        'touchstart'
    ];

    resetEvents.forEach(event => {
        document.addEventListener(event, resetTimer, true);
    });

    // Iniciar temporizadores
    resetTimer();

    // Exportar función de logout manual si se necesita
    window.manualLogout = performLogout;
}

// Ejecutar cuando el DOM esté cargado
document.addEventListener('DOMContentLoaded', setupSessionTimeout);
