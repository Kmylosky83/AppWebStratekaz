let currentStep = 1;
let userType = null;
let companyType = null;
const totalSteps = 4;

// Lista de departamentos de Colombia
const departamentos = [
    'Amazonas', 'Antioquia', 'Arauca', 'Atlántico', 'Bolívar', 'Boyacá', 
    'Caldas', 'Caquetá', 'Casanare', 'Cauca', 'Cesar', 'Chocó', 'Córdoba', 
    'Cundinamarca', 'Guainía', 'Guaviare', 'Huila', 'La Guajira', 'Magdalena', 
    'Meta', 'Nariño', 'Norte de Santander', 'Putumayo', 'Quindío', 'Risaralda', 
    'San Andrés y Providencia', 'Santander', 'Sucre', 'Tolima', 'Valle del Cauca', 
    'Vaupés', 'Vichada'
];

// Lista de industrias
const industrias = [
    'Minería y Energía', 'Industria Manufacturera', 'Agricultura y Ganadería',
    'Pesca y Acuicultura', 'Construcción', 'Comercio', 'Transporte y Logística',
    'Turismo', 'Tecnología e Innovación', 'Servicios Financieros y Seguros',
    'Salud y Bienestar', 'Educación', 'Arte y Cultura', 'Medios de Comunicación',
    'Servicios Profesionales', 'Sector Inmobiliario', 'Agroindustria',
    'Servicios Públicos'
];

function selectUserType(type) {
    userType = type;
    // Remover selección previa
    document.querySelectorAll('.user-type-card').forEach(card => {
        card.classList.remove('selected');
        card.style.borderColor = '';
    });
    
    // Marcar la selección actual
    const selectedCard = event.currentTarget;
    selectedCard.classList.add('selected');
    selectedCard.style.borderColor = '#ec268f';
    
    // Habilitar el botón siguiente
    document.getElementById('nextBtn').classList.remove('disabled');
}

function selectCompanyType(type) {
    companyType = type;
    document.querySelectorAll('.company-type-card').forEach(card => {
        card.classList.remove('selected');
        card.style.borderColor = '';
    });
    
    const selectedCard = event.currentTarget;
    selectedCard.classList.add('selected');
    selectedCard.style.borderColor = '#ec268f';
    
    document.getElementById('nextBtn').classList.remove('disabled');
}

function validateCurrentStep() {
    switch(currentStep) {
        case 1:
            // Validar selección de tipo de usuario
            if (!userType) {
                Swal.fire({
                    icon: 'warning',
                    title: 'Selección requerida',
                    text: 'Por favor, selecciona un tipo de usuario para continuar.'
                });
                return false;
            }
            return true;

            case 2: // Cuando estamos en el paso 2 del formulario
            if (userType === 'professional') { // Si es un profesional independiente
                // Obtener referencias a los elementos del formulario
                const form = document.getElementById('professionalForm');
                const password = form.querySelector('input[name="password"]');
                const confirmPassword = form.querySelector('input[name="password_confirm"]');
                const email = form.querySelector('input[name="email"]');

                // Validar el email
                if (!validateEmailInRealTime(email)) {
                    showValidationMessage(email, 'Por favor ingrese un correo electrónico válido');
                    return false;
                }

                // Validar que las contraseñas coincidan
                if (!validatePasswordMatch(password, confirmPassword)) {
                    showValidationMessage(confirmPassword, 'Las contraseñas no coinciden');
                    return false;
                }

                // Si no pasa la validación general del formulario
                if (!form.checkValidity()) {
                    form.classList.add('was-validated');
                    showValidationMessage(form, 'Por favor complete todos los campos requeridos');
                    return false;
                }
            }
            return true;

        case 3:
            const form = userType === 'company' ? 
                document.getElementById('companyForm') : 
                document.getElementById('verificationForm');
            if (form && !form.checkValidity()) {
                form.classList.add('was-validated');
                Swal.fire({
                    icon: 'warning',
                    title: 'Campos requeridos',
                    text: 'Por favor, completa todos los campos requeridos.'
                });
                return false;
            }
            return true;

        case 4:
            const verificationForm = document.getElementById('verificationForm');
            if (verificationForm && !verificationForm.checkValidity()) {
                verificationForm.classList.add('was-validated');
                Swal.fire({
                    icon: 'warning',
                    title: 'Verificación requerida',
                    text: 'Por favor, acepta los términos y condiciones para continuar.'
                });
                return false;
            }
            return true;
    }
    return true;
}

function nextStep() {
    if (!validateCurrentStep()) return;
    
    currentStep++;
    updateStepDisplay();
}

function prevStep() {
    if (currentStep > 1) {
        currentStep--;
        updateStepDisplay();
    }
}

function updateStepDisplay() {
    // Ocultar todos los pasos
    document.querySelectorAll('.step').forEach(step => step.classList.add('d-none'));
    
    // Mostrar el paso actual
    const stepDiv = document.getElementById(`step${currentStep}`);
    if (stepDiv) {
        stepDiv.classList.remove('d-none');
    }
    
    // Actualizar barra de progreso
    const progress = ((currentStep - 1) / (totalSteps - 1)) * 100;
    document.getElementById('progress-bar').style.width = `${progress}%`;
    
    // Actualizar visibilidad de botones
    document.getElementById('prevBtn').classList.toggle('d-none', currentStep === 1);
    
    // Si es el último paso, cambiar el texto del botón
    const nextBtn = document.getElementById('nextBtn');
    nextBtn.textContent = currentStep === totalSteps ? 'Completar Registro' : 'Siguiente';
    
    // Actualizar contenido según el paso
    updateStepContent();
}

function updateStepContent() {
    const stepDiv = document.getElementById(`step${currentStep}`);
    if (!stepDiv) return;
    
    switch(currentStep) {
        case 2:
            if (userType === 'company') {
                stepDiv.innerHTML = getCompanyTypeHTML();
            } else {
                stepDiv.innerHTML = getProfessionalFormHTML();
            }
            break;
        case 3:
            if (userType === 'company') {
                stepDiv.innerHTML = getCompanyFormHTML();
            } else {
                stepDiv.innerHTML = getVerificationHTML();
            }
            break;
        case 4:
            stepDiv.innerHTML = getVerificationHTML();
            break;
    }
    
    // Inicializar validación después de actualizar el contenido
    initializeFormValidation();
}

function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
}
// HTML Templates
function getProfessionalFormHTML() {
    return `
        <h5 class="text-center mb-4">Información Personal</h5>
        <form id="professionalForm" class="needs-validation" novalidate>
            <div class="row g-3">
                <div class="col-md-6">
                    <label class="form-label">Nombres</label>
                    <input type="text" class="form-control" name="nombres" required>
                </div>
                <div class="col-md-6">
                    <label class="form-label">Apellidos</label>
                    <input type="text" class="form-control" name="apellidos" required>
                </div>
                <div class="col-md-6">
                    <label class="form-label">Correo electrónico</label>
                    <input type="email" 
                           class="form-control" 
                           name="email" 
                           oninput="validateEmailInRealTime(this)"
                           required>
                    <div class="invalid-feedback">
                        Por favor ingrese un correo electrónico válido
                    </div>
                </div>
                <div class="col-md-6">
                    <label class="form-label">Profesión</label>
                    <input type="text" class="form-control" name="profesion" required>
                </div>
                <div class="col-md-6">
                    <label class="form-label">Número de Contacto</label>
                    <input type="text" 
                           class="form-control" 
                           name="contact_phone" 
                           pattern="[0-9]{10}" 
                           maxlength="10" 
                           onkeypress="return event.charCode >= 48 && event.charCode <= 57"
                           title="Ingrese un número de teléfono válido de 10 dígitos"
                           required>
                    <div class="invalid-feedback">
                        Por favor ingrese un número de teléfono válido de 10 dígitos
                    </div>
                </div>
                <div class="col-md-6">
                    <label class="form-label">Ciudad</label>
                    <input type="text" class="form-control" name="ciudad" required>
                </div>
                <div class="col-12">
                    <label class="form-label">Departamento</label>
                    <select class="form-select" name="departamento" required>
                        <option value="">Seleccione...</option>
                        ${departamentos.map(dep => `<option value="${dep}">${dep}</option>`).join('')}
                    </select>
                </div>
                <div class="col-md-6">
                    <label class="form-label">Contraseña</label>
                    <div class="input-group">
                        <input type="password" 
                            class="form-control" 
                            name="password" 
                            id="password_prof"
                            required
                            oninput="validatePasswordStrength(this.value)">
                        <button class="btn btn-outline-secondary" type="button" onclick="togglePassword('password_prof')">
                            <i class="fas fa-eye"></i>
                        </button>
                    </div>
                    <div class="mt-2">
                        <div class="progress" style="height: 3px;">
                            <div id="password-strength-prof" class="progress-bar" role="progressbar"></div>
                        </div>
                        <div class="d-flex justify-content-between mt-1 small">
                            <span data-requirement="8+" class="text-muted"><i class="fas fa-circle"></i> 8+</span>
                            <span data-requirement="ABC" class="text-muted"><i class="fas fa-circle"></i> ABC</span>
                            <span data-requirement="abc" class="text-muted"><i class="fas fa-circle"></i> abc</span>
                            <span data-requirement="123" class="text-muted"><i class="fas fa-circle"></i> 123</span>
                            <span data-requirement="@#$" class="text-muted"><i class="fas fa-circle"></i> @#$</span>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <label class="form-label">Confirmar Contraseña</label>
                    <div class="input-group">
                        <input type="password" 
                            class="form-control" 
                            name="password_confirm" 
                            id="password_confirm_prof"
                            required
                            oninput="validatePasswordMatch('password_prof', 'password_confirm_prof')">
                        <button class="btn btn-outline-secondary" type="button" onclick="togglePassword('password_confirm_prof')">
                            <i class="fas fa-eye"></i>
                        </button>
                    </div>
                    <div class="invalid-feedback">Las contraseñas no coinciden</div>
                </div>
            </div>
        </form>
    `;
}

// Continúa el código...
function getCompanyTypeHTML() {
    return `
        <h5 class="text-center mb-4">¿Qué tipo de empresa eres?</h5>
        <div class="row g-4">
            <div class="col-md-6">
                <div class="card h-100 company-type-card" onclick="selectCompanyType('direct')">
                    <div class="card-body text-center p-4">
                        <i class="fas fa-building fa-3x mb-3"></i>
                        <h6>Empresa Directa</h6>
                        <p class="small text-muted">Usa el software para sus propias actividades</p>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card h-100 company-type-card" onclick="selectCompanyType('consultant')">
                    <div class="card-body text-center p-4">
                        <i class="fas fa-handshake fa-3x mb-3"></i>
                        <h6>Consultora</h6>
                        <p class="small text-muted">Ofrece servicios de consultoría</p>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function getCompanyFormHTML() {
    return `
        <h5 class="text-center mb-4">Información de la Empresa</h5>
        <form id="companyForm" class="needs-validation" novalidate>
            <div class="row g-3">
                <div class="col-12">
                    <label class="form-label">Nombre de la Empresa</label>
                    <input type="text" class="form-control" name="company_name" required>
                </div>
                <div class="col-md-6">
                    <label class="form-label">NIT (sin dígito de verificación)</label>
                    <input type="text" 
                           class="form-control" 
                           name="nit" 
                           pattern="[0-9]{9}" 
                           maxlength="9" 
                           onkeypress="return event.charCode >= 48 && event.charCode <= 57"
                           title="Ingrese un NIT válido de 9 dígitos sin dígito de verificación"
                           required>
                    <div class="invalid-feedback">
                        Por favor ingrese un NIT válido de 9 dígitos
                    </div>
                </div>
                <div class="col-md-6">
                    <label class="form-label">Industria o Sector</label>
                    <select class="form-select" name="industry" required>
                        <option value="">Seleccione...</option>
                        ${industrias.map(ind => `<option value="${ind}">${ind}</option>`).join('')}
                    </select>
                </div>
                <div class="col-md-6">
                    <label class="form-label">Ciudad</label>
                    <input type="text" class="form-control" name="ciudad" required>
                </div>
                <div class="col-md-6">
                    <label class="form-label">Departamento</label>
                    <select class="form-select" name="departamento" required>
                        <option value="">Seleccione...</option>
                        ${departamentos.map(dep => `<option value="${dep}">${dep}</option>`).join('')}
                    </select>
                </div>
                <div class="col-12"><hr></div>
                <div class="col-12">
                    <h6>Datos de Contacto</h6>
                </div>
                <div class="col-md-6">
                    <label class="form-label">Nombres</label>
                    <input type="text" class="form-control" name="contact_first_name" required>
                </div>
                <div class="col-md-6">
                    <label class="form-label">Apellidos</label>
                    <input type="text" class="form-control" name="contact_last_name" required>
                </div>
                <div class="col-md-6">
                    <label class="form-label">Cargo o Rol</label>
                    <input type="text" class="form-control" name="contact_position" required>
                </div>
                <div class="col-md-6">
                    <label class="form-label">Correo Electrónico</label>
                    <input type="email" class="form-control" name="contact_email" required>
                </div>
                <div class="col-md-6">
                    <label class="form-label">Número de contacto</label>
                    <input type="text" 
                           class="form-control" 
                           name="telefono" 
                           pattern="[0-9]{10}" 
                           maxlength="10" 
                           onkeypress="return event.charCode >= 48 && event.charCode <= 57"
                           title="Ingrese un número de teléfono válido de 10 dígitos"
                           required>
                    <div class="invalid-feedback">
                        Por favor ingrese un número de teléfono válido de 10 dígitos
                    </div>
                </div>
                <div class="col-md-6">
                    <label class="form-label">Contraseña</label>
                    <div class="input-group">
                        <input type="password" 
                            class="form-control" 
                            name="password" 
                            id="password_company"
                            pattern="^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
                            oninput="updatePasswordStrength(this.value)"
                            required>
                        <button class="btn btn-outline-secondary" type="button" onclick="togglePassword('password_company')">
                            <i class="fas fa-eye"></i>
                        </button>
                    </div>
                    <div class="progress mt-2" style="height: 5px;">
                        <div id="password-strength" class="progress-bar" role="progressbar" style="width: 0%"></div>
                    </div>
                    <div class="password-requirements small text-muted mt-1">
                        <div id="req-length"><i class="fas fa-circle"></i> Mínimo 8 caracteres</div>
                        <div id="req-uppercase"><i class="fas fa-circle"></i> Una mayúscula</div>
                        <div id="req-lowercase"><i class="fas fa-circle"></i> Una minúscula</div>
                        <div id="req-number"><i class="fas fa-circle"></i> Un número</div>
                        <div id="req-special"><i class="fas fa-circle"></i> Un carácter especial</div>
                    </div>
                </div>
                </div>
                <div class="col-md-6">
                    <label class="form-label">Confirmar Contraseña</label>
                    <input type="password" class="form-control" name="password_confirm" required>
                </div>
            </div>
        </form>
    `;
}

function getVerificationHTML() {
    return `
        <h5 class="text-center mb-4">Verificación Final</h5>
        <form id="verificationForm" class="needs-validation" novalidate>
            <div class="mb-4">
                <div class="g-recaptcha" data-sitekey="TU_CLAVE_RECAPTCHA"></div>
            </div>
            <div class="mb-3 form-check">
                <input type="checkbox" class="form-check-input" id="terms" required>
                <label class="form-check-label" for="terms">
                    Acepto los <a href="#" data-bs-toggle="modal" data-bs-target="#termsModal">Términos y Condiciones</a>
                </label>
            </div>
            <div class="mb-3 form-check">
                <input type="checkbox" class="form-check-input" id="privacy" required>
                <label class="form-check-label" for="privacy">
                    Acepto la <a href="#" data-bs-toggle="modal" data-bs-target="#privacyModal">Política de Privacidad</a>
                </label>
            </div>
            <div class="d-grid">
                <button type="submit" class="btn btn-primary">Completar Registro</button>
            </div>
        </form>
    `;
}

function validatePassword(password, confirmPassword) {
    const input = document.getElementById('password');
    const requirements = {
        length: password.length >= 8,
        uppercase: /[A-Z]/.test(password),
        lowercase: /[a-z]/.test(password),
        number: /\d/.test(password),
        special: /[@$!%*?&]/.test(password)
    };

    const isValid = Object.values(requirements).every(Boolean);
    
    if (isValid) {
        input.classList.add('is-valid');
        input.classList.remove('is-invalid');
        return true;
    } else {
        input.classList.add('is-invalid');
        input.classList.remove('is-valid');
        return false;
    }
}

function validatePasswordStrength(password) {
    // Definir los criterios
    const criteria = {
        minLength: password.length >= 8,
        hasUpperCase: /[A-Z]/.test(password),
        hasLowerCase: /[a-z]/.test(password),
        hasNumbers: /\d/.test(password),
        hasSpecialChar: /[@$!%*?&#]/.test(password)
    };

    // Actualizar cada indicador individualmente
    const indicators = {
        '8+': criteria.minLength,
        'ABC': criteria.hasUpperCase,
        'abc': criteria.hasLowerCase,
        '123': criteria.hasNumbers,
        '@#$': criteria.hasSpecialChar
    };

    // Actualizar los indicadores visuales
    Object.entries(indicators).forEach(([key, isValid]) => {
        const indicator = document.querySelector(`[data-requirement="${key}"]`);
        if (indicator) {
            indicator.classList.toggle('text-success', isValid);
            indicator.classList.toggle('text-muted', !isValid);
        }
    });

    // Calcular fortaleza total
    const strength = Object.values(criteria).filter(Boolean).length;
    const strengthBar = document.getElementById('password-strength-prof');
    
    if (strengthBar) {
        const percentage = (strength / 5) * 100;
        strengthBar.style.width = `${percentage}%`;
        
        // Actualizar color de la barra
        strengthBar.className = 'progress-bar';
        if (strength <= 2) {
            strengthBar.classList.add('bg-danger');
        } else if (strength <= 4) {
            strengthBar.classList.add('bg-warning');
        } else {
            strengthBar.classList.add('bg-success');
        }
    }

    return strength === 5;
}

function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    const button = input.nextElementSibling;
    const icon = button.querySelector('i');
    
    if (input.type === 'password') {
        input.type = 'text';
        icon.className = 'fas fa-eye-slash';
    } else {
        input.type = 'password';
        icon.className = 'fas fa-eye';
    }
}

// Agregar esta función
function validateEmailInRealTime(input) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const isValid = emailRegex.test(input.value);
    const feedbackDiv = input.nextElementSibling;
    
    if (isValid) {
        input.classList.add('is-valid');
        input.classList.remove('is-invalid');
        return true;
    } else {
        input.classList.add('is-invalid');
        input.classList.remove('is-valid');
        return false;
    }
}

function validatePasswordMatch(passwordId, confirmPasswordId) {
    const password = document.getElementById(passwordId);
    const confirmPassword = document.getElementById(confirmPasswordId);
    
    const isMatch = password && confirmPassword && password.value === confirmPassword.value;
    
    if (confirmPassword) {
        if (isMatch) {
            confirmPassword.classList.add('is-valid');
            confirmPassword.classList.remove('is-invalid');
        } else {
            confirmPassword.classList.add('is-invalid');
            confirmPassword.classList.remove('is-valid');
        }
    }
    
    return isMatch;
}

function showValidationMessage(input, message, type = 'error') {
    Swal.fire({
        icon: type === 'error' ? 'error' : 'warning',
        title: type === 'error' ? 'Error de validación' : 'Atención',
        text: message,
        toast: true,
        position: 'top-end',
        showConfirmButton: false,
        timer: 3000,
        timerProgressBar: true
    });
}

function validatePasswordStrength(password) {
    const criteria = {
        minLength: password.length >= 8,
        hasUpperCase: /[A-Z]/.test(password),
        hasLowerCase: /[a-z]/.test(password),
        hasNumbers: /\d/.test(password),
        hasSpecialChar: /[!@#$%^&*]/.test(password)
    };

    const strength = Object.values(criteria).filter(Boolean).length;

    // Actualizar indicadores visuales
    Object.keys(criteria).forEach(key => {
        const element = document.getElementById(`password-req-${key}`);
        if (element) {
            if (criteria[key]) {
                element.classList.remove('text-muted');
                element.classList.add('text-success');
                element.querySelector('i').className = 'fas fa-check-circle';
            } else {
                element.classList.add('text-muted');
                element.classList.remove('text-success');
                element.querySelector('i').className = 'fas fa-circle';
            }
        }
    });

    // Actualizar barra de progreso
    const strengthBar = document.getElementById('password-strength-prof');
    if (strengthBar) {
        const percentage = (strength / 5) * 100;
        strengthBar.style.width = `${percentage}%`;
        
        if (strength <= 2) {
            strengthBar.className = 'progress-bar bg-danger';
        } else if (strength <= 4) {
            strengthBar.className = 'progress-bar bg-warning';
        } else {
            strengthBar.className = 'progress-bar bg-success';
        }
    }

    return strength === 5;
}

function handlePasswordInput(input) {
    const password = input.value;
    const isValid = validatePasswordStrength(password);
    
    if (isValid) {
        input.classList.add('is-valid');
        input.classList.remove('is-invalid');
    } else {
        input.classList.remove('is-valid');
        input.classList.add('is-invalid');
    }
    
    // Validar confirmación si existe
    const confirmInput = document.getElementById('password_confirm_prof');
    if (confirmInput && confirmInput.value) {
        validatePasswordMatch('password_prof', 'password_confirm_prof');
    }
}
   
// Agregar al final del archivo
document.addEventListener('DOMContentLoaded', function() {
    // Event listener para contraseña
    const passwordInput = document.getElementById('password_prof');
    if (passwordInput) {
        passwordInput.addEventListener('input', function() {
            validatePasswordStrength(this.value);
        });
    }
});