// Cifrar archivo
document.getElementById("cifrarForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const fileInput = document.getElementById("fileToEncrypt");
    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    const response = await fetch("http://127.0.0.1:5000/cifrar", {
        method: "POST",
        body: formData,
    });

    const result = await response.json();
    document.getElementById("result").innerText = "Archivo cifrado: " + result.archivo_cifrado;
});

// Descifrar archivo
document.getElementById("descifrarForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const fileInput = document.getElementById("fileToDecrypt");
    const keyInput = document.getElementById("keyFile");
    const formData = new FormData();
    formData.append("file", fileInput.files[0]);
    formData.append("key", keyInput.files[0]);

    const response = await fetch("http://127.0.0.1:5000/descifrar", {
        method: "POST",
        body: formData,
    });

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "archivo_descifrado";
    a.click();
});

// Enviar mensaje al foro
document.getElementById("forumForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const messageInput = document.getElementById("forumMessage");
    const message = messageInput.value;

    const response = await fetch("http://127.0.0.1:5000/foro", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ message }),
    });

    const result = await response.json();
    if (result.success) {
        messageInput.value = ""; // Limpiar el campo de texto
        loadForumMessages(); // Recargar mensajes
    }
});

// Cargar mensajes del foro
async function loadForumMessages() {
    const response = await fetch("http://127.0.0.1:5000/foro");
    const messages = await response.json();
    const forumMessages = document.getElementById("forumMessages");
    forumMessages.innerHTML = messages.map(msg => `<div><strong>Usuario:</strong> ${msg.message}</div>`).join("");
}

// Cargar mensajes al iniciar la página
loadForumMessages();