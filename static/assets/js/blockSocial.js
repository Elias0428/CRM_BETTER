function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener('DOMContentLoaded', () => {
    const csrfToken = getCookie('csrftoken'); // Obtener el token CSRF de la cookie

    document.getElementById('show-full-social').addEventListener('click', () => {
        document.getElementById('password-modal').style.display = 'block';
        document.getElementById('password-input').focus();
    });

    document.getElementById('submit-password').addEventListener('click', async (event) => {
        event.preventDefault();
        const key = document.getElementById('password-input').value;

        if (key) {
            try {
                const response = await fetch(window.location.href, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': csrfToken,
                    },
                    body: new URLSearchParams({
                        key: key,
                        action: 'validate_key',
                    }),
                });

                if (!response.ok) {
                    alert(`Error: ${response.status} - ${response.statusText}`);
                    return;
                }

                const data = await response.json();

                if (data.status === 'success') {
                    const formattedSocial = formatSocialSecurityNumber(data.social);
                    const socialField = document.getElementById('social_security');
                    socialField.value = formattedSocial;
                    socialField.focus();
                    document.getElementById('password-modal').style.display = 'none';
                    document.getElementById('password-input').value = '';
                } else {
                    alert(data.message);
                }
            } catch (error) {
                console.error('Error en la solicitud fetch:', error);
                alert('Hubo un error. Intenta nuevamente.');
            }
        } else {
            alert('Por favor, ingresa una clave.');
        }
    });

    document.getElementById('cancel-password').addEventListener('click', (event) => {
        event.preventDefault();
        document.getElementById('password-modal').style.display = 'none';
        document.getElementById('password-input').value = '';
    });

    function formatSocialSecurityNumber(number) {
        if (number.length === 9) {
            return `${number.slice(0, 3)}-${number.slice(3, 5)}-${number.slice(5)}`;
        }
        return number;
    }
});
