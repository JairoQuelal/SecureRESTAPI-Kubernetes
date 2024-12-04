const API_BASE = "http://localhost:5000";

// Manejo centralizado de errores
async function handleResponse(response) {
    const result = await response.json();
    if (!response.ok) {
        throw new Error(result.msg || "Error desconocido");
    }
    return result;
}

// Reutilización de headers con token
function getHeaders(withAuth = false) {
    const headers = { "Content-Type": "application/json" };
    if (withAuth) {
        const token = localStorage.getItem("access_token");
        if (token) {
            headers.Authorization = `Bearer ${token}`;
        }
    }
    return headers;
}

// Redirección y mensajes
function redirectToLogin() {
    alert("Debe iniciar sesión para continuar.");
    window.location.href = "/login";
}

// Validación de formularios
function validateRegistrationForm(username, password, role) {
    if (!username || !password || !role) {
        alert("Todos los campos son obligatorios.");
        return false;
    }
    return true;
}

// Registro de usuarios
async function registerUser(username, password, role) {
    if (!validateRegistrationForm(username, password, role)) return;

    try {
        const response = await fetch(`${API_BASE}/register`, {
            method: "POST",
            headers: getHeaders(),
            body: JSON.stringify({ username, password, role })
        });
        const result = await handleResponse(response);
        alert(result.msg);
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

// Inicio de sesión
async function loginUser(username, password) {
    try {
        const response = await fetch(`${API_BASE}/login`, {
            method: "POST",
            headers: getHeaders(),
            body: JSON.stringify({ username, password })
        });
        const result = await handleResponse(response);

        // Guardar el token en localStorage y redirigir
        localStorage.setItem("access_token", result.access_token);
        alert("Inicio de sesión exitoso");
        window.location.href = "/courses";
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

// Creación de cursos
async function createCourse(courseData) {
    try {
        const response = await fetch(`${API_BASE}/courses`, {
            method: "POST",
            headers: getHeaders(true),
            body: JSON.stringify(courseData)
        });
        const result = await handleResponse(response);
        alert(result.msg);
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

// Obtener la lista de cursos
async function fetchCourses() {
    const token = localStorage.getItem("access_token");
    if (!token) {
        redirectToLogin();
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/courses`, {
            method: "GET",
            headers: getHeaders(true),
        });

        const text = await response.text(); // Obtén el texto bruto de la respuesta
        try {
            const courses = JSON.parse(text); // Intenta parsear el JSON
            if (response.ok) {
                displayCourses(courses);
            } else {
                if (response.status === 401) {
                    redirectToLogin();
                } else {
                    alert(`Error al obtener cursos: ${courses.msg}`);
                }
            }
        } catch (e) {
            console.error("Respuesta no es JSON:", text);
            alert("Ocurrió un error inesperado al procesar la respuesta.");
        }
    } catch (error) {
        console.error("Error al obtener los cursos:", error);
        alert("Ocurrió un error inesperado.");
    }
}


// Mostrar la lista de cursos en la página
function displayCourses(courses) {
    const courseList = document.getElementById("courseList");
    courseList.innerHTML = ""; // Limpiar la lista actual

    if (courses.length === 0) {
        courseList.innerHTML = "<p>No hay cursos disponibles.</p>";
        return;
    }

    courses.forEach((course) => {
        const courseItem = document.createElement("div");
        courseItem.classList.add("course-item");
        courseItem.innerHTML = `
            <h3>${course.title}</h3>
            <p><strong>Descripción:</strong> ${course.description || "No disponible"}</p>
            <p><strong>Instructor:</strong> ${course.instructor}</p>
            <p><strong>Duración:</strong> ${course.duration} horas</p>
            <p><strong>Límite de Inscripción:</strong> ${course.enrollment_limit || "Sin límite"}</p>
        `;
        courseList.appendChild(courseItem);
    });
}
