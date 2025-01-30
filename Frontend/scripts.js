// Configuración de Firebase
const firebaseConfig = {
  apiKey: "AIzaSyDjN9GrRjVYSIWbBdxP9UfHHuvLZI_HxOI",
  authDomain: "encriptacion-y-miniforo.firebaseapp.com",
  projectId: "encriptacion-y-miniforo",
  storageBucket: "encriptacion-y-miniforo.firebasestorage.app",
  messagingSenderId: "244974934559",
  appId: "1:244974934559:web:40c6db4e2b9876eef4932a",
};

// Inicializar Firebase
firebase.initializeApp(firebaseConfig);
const auth = firebase.auth();

// Estado del usuario
let user = null;

// Iniciar sesión con Google
document.getElementById("google-login").addEventListener("click", () => {
    const provider = new firebase.auth.GoogleAuthProvider();
    auth.signInWithPopup(provider)
        .then((result) => {
            user = result.user;
            updateUI();
        })
        .catch((error) => {
            console.error("Error al iniciar sesión:", error);
        });
});

// Cerrar sesión
document.getElementById("logout").addEventListener("click", () => {
    auth.signOut()
        .then(() => {
            user = null;
            updateUI();
        })
        .catch((error) => {
            console.error("Error al cerrar sesión:", error);
        });
});

// Actualizar la interfaz de usuario
function updateUI() {
    const authSection = document.getElementById("auth-section");
    const userInfo = document.getElementById("user-info");
    const userNickname = document.getElementById("user-nickname");

    if (user) {
        authSection.querySelector("button").style.display = "none";
        userInfo.style.display = "block";
        userNickname.textContent = user.displayName || user.email;
    } else {
        authSection.querySelector("button").style.display = "block";
        userInfo.style.display = "none";
    }
}

// Escuchar cambios en la autenticación
auth.onAuthStateChanged((u) => {
    user = u;
    updateUI();
});

// Enviar mensaje al foro
document.getElementById("forumForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!user) {
        alert("Debes iniciar sesión para enviar mensajes.");
        return;
    }

    const messageInput = document.getElementById("forumMessage");
    const message = messageInput.value;

    const response = await fetch("http://127.0.0.1:5000/foro", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            message,
            nickname: user.displayName || user.email,
        }),
    });

    const result = await response.json();
    if (result.success) {
        messageInput.value = ""; // Limpiar el campo de texto
        loadForumMessages(); // Recargar mensajes
    }
});

// Cargar mensajes del foro
async function loadForumMessages() {
    const response = await fetch("http://localhost:5000/foro");
    const messages = await response.json();
    const forumMessages = document.getElementById("forumMessages");
    forumMessages.innerHTML = messages.map(msg => `
        <div>
            <strong>${msg.nickname}:</strong> ${msg.message}
        </div>
    `).join("");
}

// Cargar mensajes al iniciar la página
loadForumMessages();