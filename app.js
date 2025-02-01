// Obtener la URL de autenticación del backend
async function loginWithGoogle() {
    try {
        const response = await fetch("http://localhost:3000/api/login/google");
        const data = await response.json();

        // Abre la URL de Google en una nueva ventana
        const authWindow = window.open(data.url, "Google Auth", "width=500,height=600");

        // Escucha el mensaje del callback
        window.addEventListener("message", (event) => {
            if (event.origin === "http://localhost:3000") {
                const { token, user } = event.data;
                localStorage.setItem("jwt_token", token);
                showUserInfo(user);
                authWindow.close();
            }
        });
    } catch (error) {
        console.error("Error:", error);
    }
}

// Manejar el cierre de sesión
async function logout() {
    localStorage.removeItem("jwt_token");
    window.location.reload();
}

// Mostrar información del usuario
async function showUserInfo(user) {
    const userInfoDiv = document.getElementById("user-info");
    userInfoDiv.innerHTML = `
        <p class="text-lg">Bienvenido, <span class="font-semibold">${user.name}</span>!</p>
        <img src="${user.picture}" class="w-16 h-16 rounded-full mt-2" alt="User Image">
    `;
    userInfoDiv.classList.remove("hidden");
}

// Verificar el token al cargar la página
window.onload = async() => {
    const token = localStorage.getItem("jwt_token");
    if (token) {
        try {
            const response = await fetch("http://localhost:3000/api/me", {
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            });
            const user = await response.json();
            showUserInfo(user);
        } catch (error) {
            console.error("Error:", error);
        }
    }
};