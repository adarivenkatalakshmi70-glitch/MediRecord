(function () {
    const phonePattern = /^(?:\+91[-\s]?)?[6-9]\d{9}$/;
    const patientIdPattern = /^P\d{4,}$/i;

    function showError(input, message) {
        input.setCustomValidity(message);
        input.reportValidity();
    }

    document.querySelectorAll("form.needs-validation").forEach(function (form) {
        form.addEventListener("submit", function (event) {
            const isPatientForm = form.getAttribute("data-validate-patient") === "true";
            const isEdit = form.getAttribute("data-edit") === "true";

            if (isPatientForm) {
                const name = form.querySelector("#name");
                const phone = form.querySelector("#phone");
                const emergency = form.querySelector("#emergency_contact");
                const dob = form.querySelector("#date_of_birth");
                const patientId = form.querySelector("#patient_id");

                if (name && (!name.value.trim() || name.value.trim().length < 2)) {
                    showError(name, "Full name is required.");
                    event.preventDefault();
                    event.stopPropagation();
                    return;
                }
                if (name && /^\d+$/.test(name.value.replace(/\s/g, ""))) {
                    showError(name, "Name cannot contain only numbers.");
                    event.preventDefault();
                    event.stopPropagation();
                    return;
                }
                if (phone && !phonePattern.test(phone.value.trim())) {
                    showError(phone, "Enter a valid 10-digit Indian mobile number.");
                    event.preventDefault();
                    event.stopPropagation();
                    return;
                }
                if (emergency && emergency.value.trim() && !phonePattern.test(emergency.value.trim())) {
                    showError(emergency, "Enter a valid emergency contact number.");
                    event.preventDefault();
                    event.stopPropagation();
                    return;
                }
                if (dob && dob.value && new Date(dob.value) > new Date()) {
                    showError(dob, "Date of birth cannot be in the future.");
                    event.preventDefault();
                    event.stopPropagation();
                    return;
                }
                if (!isEdit && patientId && !patientIdPattern.test(patientId.value.trim())) {
                    showError(patientId, "Patient ID must look like P1001.");
                    event.preventDefault();
                    event.stopPropagation();
                    return;
                }
            }

            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add("was-validated");
        });
    });
})();
