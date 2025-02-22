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
    
    // Remover selección previa
    document.querySelectorAll('.company-type-card').forEach(card => {
        card.classList.remove('selected');
        card.style.borderColor = '';
        // Remover efectos visuales adicionales
        card.querySelector('i').style.color = '';
        card.querySelector('h6').style.color = '';
    });
    
    // Aplicar selección actual
    const selectedCard = event.currentTarget;
    selectedCard.classList.add('selected');
    selectedCard.style.borderColor = '#ec268f';
    
    // Efectos visuales adicionales
    selectedCard.querySelector('i').style.color = '#ec268f';
    selectedCard.querySelector('h6').style.color = '#ec268f';
    
    // Habilitar botón y mostrar feedback visual
    const nextBtn = document.getElementById('nextBtn');
    nextBtn.classList.remove('disabled');
    nextBtn.classList.add('pulse'); // Agregar efecto de pulso
    
    // Actualizar la barra de progreso
    updateProgressBar();
    
    // Guardar selección
    localStorage.setItem('companyType', type);
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

        case 2:
            if (userType === 'professional') {
                const form = document.getElementById('professionalForm');
                if (!form) return false;
            
                const password = form.querySelector('#password_prof');
                const confirmPassword = form.querySelector('#password_confirm_prof');
                const email = form.querySelector('input[name="email"]');
                const terms = form.querySelector('#terms_prof');
                const privacy = form.querySelector('#privacy_prof');
            
                // Validar email
                if (!validateEmailInRealTime(email)) {
                    showValidationMessage(null, 'Por favor ingrese un correo electrónico válido');
                    return false;
                }
            
                // Validar contraseña
                if (password && confirmPassword) {
                    const validation = validatePassword(password.value, confirmPassword.value, 'professional');
                    if (!validation.isValid) {
                        showValidationMessage(null, 'La contraseña debe cumplir todos los requisitos');
                        return false;
                    }
                    if (password.value !== confirmPassword.value) {
                        showValidationMessage(null, 'Las contraseñas no coinciden');
                        return false;
                    }
                }

                // Validar términos y condiciones
                if (!terms.checked || !privacy.checked) {
                    showValidationMessage(null, 'Debe aceptar los términos y condiciones y la política de privacidad');
                    return false;
                }
            
                // Validar que todos los campos requeridos estén completos
                if (!form.checkValidity()) {
                    form.classList.add('was-validated');
                    showValidationMessage(null, 'Por favor complete todos los campos requeridos');
                    return false;
                }
            
                return true;
            } else if (userType === 'company') {
                // Validación para el tipo empresa
                const companyTypeSelected = companyType !== null;
                if (!companyTypeSelected) {
                    showValidationMessage(null, 'Por favor seleccione un tipo de empresa');
                    return false;
                }
                return true;
            }
            return true;

        case 3:
            if (userType === 'company') {
                const form = document.getElementById('companyForm');
                if (!form) return false;
        
                // Validar NIT
                const nit = form.querySelector('input[name="nit"]');
                if (nit && !validateNIT(nit.value)) {
                    showValidationMessage(null, 'Por favor ingrese un NIT válido');
                    return false;
                }
        
                // Validar email corporativo
                const email = form.querySelector('input[name="contact_email"]');
                if (!validateEmailInRealTime(email)) {
                    showValidationMessage(null, 'Por favor ingrese un correo electrónico válido');
                    return false;
                }
        
                // Validar contraseña
                const password = form.querySelector('#password_company');
                const confirmPassword = form.querySelector('#password_confirm_company');
                if (password && confirmPassword) {
                    const validation = validatePassword(password.value, confirmPassword.value, 'company');
                    if (!validation.isValid) {
                        showValidationMessage(null, 'La contraseña debe cumplir todos los requisitos');
                        return false;
                    }
                    if (password.value !== confirmPassword.value) {
                        showValidationMessage(null, 'Las contraseñas no coinciden');
                        return false;
                    }
                }
        
                // Validar términos y condiciones
                const terms = form.querySelector('#terms_company');
                const privacy = form.querySelector('#privacy_company');
                if (!terms.checked || !privacy.checked) {
                    showValidationMessage(null, 'Debe aceptar los términos y condiciones y la política de privacidad');
                    return false;
                }
        
                // Validar formulario completo
                if (!form.checkValidity()) {
                    form.classList.add('was-validated');
                    showValidationMessage(null, 'Por favor complete todos los campos requeridos');
                    return false;
                }
            }
            finishRegistration();
            return true;

        case 4:
            if (userType === 'company') {
                finishRegistration();
            }
            return true;
            
        default:
            return true;
    }
}


function validateNIT(nit) {
    // Verificar que tenga 9 dígitos
    if (!/^\d{9}$/.test(nit)) return false;
    
    // Aquí puedes agregar validaciones adicionales específicas para NITs colombianos
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
                // Para profesionales, completar registro directamente
                finishRegistration();
            }
            break;
        case 4:
            if (userType === 'company') {
                finishRegistration();
            }
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
                            oninput="validatePassword(this.value, null, 'professional')">
                        <button class="btn btn-outline-secondary" type="button" onclick="togglePassword('password_prof')">
                            <i class="fas fa-eye"></i>
                        </button>
                    </div>
                    <div class="mt-2">
                        <div class="password-requirements mt-2">
                            <div class="d-flex justify-content-between gap-2">
                                <span class="badge bg-light text-dark" data-requirement="8+">
                                    <i class="fas fa-circle me-1"></i>8+
                                </span>
                                <span class="badge bg-light text-dark" data-requirement="ABC">
                                    <i class="fas fa-circle me-1"></i>ABC
                                </span>
                                <span class="badge bg-light text-dark" data-requirement="abc">
                                    <i class="fas fa-circle me-1"></i>abc
                                </span>
                                <span class="badge bg-light text-dark" data-requirement="123">
                                    <i class="fas fa-circle me-1"></i>123
                                </span>
                                <span class="badge bg-light text-dark" data-requirement="@#$">
                                    <i class="fas fa-circle me-1"></i>@#$
                                </span>
                            </div>
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
                            oninput="validatePassword(document.getElementById('password_prof').value, this.value, 'professional')">
                        <button class="btn btn-outline-secondary" type="button" onclick="togglePassword('password_confirm_prof')">
                            <i class="fas fa-eye"></i>
                        </button>
                    </div>
                    <div class="invalid-feedback">Las contraseñas no coinciden</div>
                    <div class="col-12 mt-4">
                        <div class="form-check mb-2">
                            <input class="form-check-input" type="checkbox" id="terms_prof" required>
                            <label class="form-check-label" for="terms_prof">
                                He leído y acepto los <a href="#" data-bs-toggle="modal" data-bs-target="#termsModal">Términos y Condiciones</a>
                            </label>
                        </div>
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="privacy_prof" required>
                            <label class="form-check-label" for="privacy_prof">
                                He leído y acepto la <a href="#" data-bs-toggle="modal" data-bs-target="#privacyModal">Política de Privacidad</a>
                            </label>
                        </div>
                    </div>
                </div>
            </div>
        </form>
    `;
}

function validatePassword(password, confirmPassword = null, type = 'professional') {
    // Objeto para almacenar el estado de validación
    const validation = {
        isValid: false,
        strength: 0,
        message: '',
        requirements: {
            length: password.length >= 8,
            uppercase: /[A-Z]/.test(password),
            lowercase: /[a-z]/.test(password),
            number: /\d/.test(password),
            special: /[!@#$%^&*(),.?":{}|<>]/.test(password)
        }
    };

    // Calcular fortaleza
    validation.strength = Object.values(validation.requirements).filter(Boolean).length;
    validation.isValid = validation.strength === 5;

    // Actualizar indicadores visuales
    const idPrefix = type === 'professional' ? '_prof' : '_company';
    const strengthBar = document.getElementById(`password-strength${idPrefix}`);
    const requirements = document.querySelectorAll(`[data-requirement]`);

    // Actualizar barra de progreso
    if (strengthBar) {
        const percentage = (validation.strength / 5) * 100;
        strengthBar.style.width = `${percentage}%`;
        strengthBar.setAttribute('aria-valuenow', percentage);

         // Actualizar clase y color según fortaleza
        strengthBar.className = 'progress-bar';        
        if (validation.strength <= 2) {
            strengthBar.classList.add('bg-danger');
        } else if (validation.strength <= 4) {
            strengthBar.classList.add('bg-warning');
        } else {
            strengthBar.classList.add('bg-success');
        }
    }

    // Actualizar indicadores de requisitos
    requirements.forEach(indicator => {
        const requirement = indicator.getAttribute('data-requirement');
        let isValid = false;

        switch (requirement) {
            case '8+': isValid = validation.requirements.length; break;
            case 'ABC': isValid = validation.requirements.uppercase; break;
            case 'abc': isValid = validation.requirements.lowercase; break;
            case '123': isValid = validation.requirements.number; break;
            case '@#$': isValid = validation.requirements.special; break;
        }

        indicator.classList.toggle('text-success', isValid);
        indicator.classList.toggle('text-muted', !isValid);
        const icon = indicator.querySelector('i');
        if (icon) {
            icon.className = isValid ? 'fas fa-check-circle' : 'fas fa-circle';
        }
    });

    // Validar coincidencia si hay confirmación
    if (confirmPassword !== null) {
        const confirmInput = document.getElementById(`password_confirm${idPrefix}`);
        const errorMessage = confirmInput.nextElementSibling;
        
        if (password === confirmPassword && validation.isValid) {
            confirmInput.classList.add('is-valid');
            confirmInput.classList.remove('is-invalid');
            if (errorMessage) errorMessage.style.display = 'none';
        } else {
            confirmInput.classList.add('is-invalid');
            confirmInput.classList.remove('is-valid');
            if (errorMessage) {
                errorMessage.textContent = password !== confirmPassword ? 
                    'Las contraseñas no coinciden' : 
                    'La contraseña no cumple con los requisitos mínimos';
                errorMessage.style.display = 'block';
            }
        }
    }

    return validation;
}

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
                <div class="col-12">
                    <hr class="my-4">
                    <h6 class="mb-3">Seguridad de la cuenta</h6>
                </div>
                <div class="col-md-6">
                    <label class="form-label">Contraseña</label>
                    <div class="input-group">
                        <input type="password" 
                            class="form-control" 
                            name="password" 
                            id="password_company"
                            required
                            oninput="validatePassword(this.value, null, 'company')">
                        <button class="btn btn-outline-secondary" type="button" onclick="togglePassword('password_company')">
                            <i class="fas fa-eye"></i>
                        </button>
                    </div>
                    <div class="password-requirements mt-2">
                        <div class="d-flex justify-content-between gap-2">
                            <span class="badge bg-light text-dark" data-requirement="8+">
                                <i class="fas fa-circle me-1"></i>8+
                            </span>
                            <span class="badge bg-light text-dark" data-requirement="ABC">
                                <i class="fas fa-circle me-1"></i>ABC
                            </span>
                            <span class="badge bg-light text-dark" data-requirement="abc">
                                <i class="fas fa-circle me-1"></i>abc
                            </span>
                            <span class="badge bg-light text-dark" data-requirement="123">
                                <i class="fas fa-circle me-1"></i>123
                            </span>
                            <span class="badge bg-light text-dark" data-requirement="@#$">
                                <i class="fas fa-circle me-1"></i>@#$
                            </span>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <label class="form-label">Confirmar Contraseña</label>
                    <div class="input-group">
                        <input type="password" 
                            class="form-control" 
                            name="password_confirm" 
                            id="password_confirm_company"
                            required
                            oninput="validatePassword(document.getElementById('password_company').value, this.value, 'company')">
                        <button class="btn btn-outline-secondary" type="button" onclick="togglePassword('password_confirm_company')">
                            <i class="fas fa-eye"></i>
                        </button>
                    </div>
                    <div class="invalid-feedback">Las contraseñas no coinciden</div>
                </div>
                <div class="col-12 mt-4">
                    <div class="form-check mb-2">
                        <input class="form-check-input" type="checkbox" id="terms_company" required>
                        <label class="form-check-label" for="terms_company">
                            He leído y acepto los <a href="#" data-bs-toggle="modal" data-bs-target="#termsModal">Términos y Condiciones</a>
                        </label>
                    </div>
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" id="privacy_company" required>
                        <label class="form-check-label" for="privacy_company">
                            He leído y acepto la <a href="#" data-bs-toggle="modal" data-bs-target="#privacyModal">Política de Privacidad</a>
                        </label>
                    </div>
                </div>
            </div>
        </form>
    `;
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

function finishRegistration() {
    // Ocultar toda la tarjeta del formulario
    const card = document.querySelector('.card');
    if (card) {
        card.style.display = 'none';
    }

    // Ocultar los botones de navegación
    const buttons = document.querySelector('.d-flex.justify-content-between');
    if (buttons) {
        buttons.style.display = 'none';
    }

    Swal.fire({
        icon: 'success',
        title: '¡Registro exitoso!',
        text: 'Tu cuenta ha sido creada correctamente.',
        showConfirmButton: false,
        timer: 2000,
        backdrop: 'rgba(255, 255, 255, 0.9)',
        customClass: {
            popup: 'swal-custom-popup'
        },
        didClose: () => {
            window.location.href = '/auth/login';
        }
    });
}