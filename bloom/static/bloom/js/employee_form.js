document.addEventListener('DOMContentLoaded', function () {
    const roleSelect = document.getElementById('id_role')
    const processOrders = document.getElementById('id_can_process_orders')
    const arrangeFlowers = document.getElementById('id_can_arrange_flowers')
    const deliverOrders = document.getElementById('id_can_deliver_orders')
    const manageStaff = document.getElementById('id_can_manage_staff')

    if (roleSelect) {
        roleSelect.addEventListener('change', function () {
            const selectedRole = this.value

            // Reset all capabilities
            processOrders.checked = false
            arrangeFlowers.checked = false
            deliverOrders.checked = false
            manageStaff.checked = false

            // Set capabilities based on role
            switch (selectedRole) {
                case 'manager':
                    processOrders.checked = true
                    manageStaff.checked = true
                    break
                case 'designer':
                    processOrders.checked = true
                    arrangeFlowers.checked = true
                    break
                case 'arranger':
                    arrangeFlowers.checked = true
                    break
                case 'delivery':
                    deliverOrders.checked = true
                    break
                case 'sales':
                    processOrders.checked = true
                    break
            }
        })
    }

    // Toggle user creation section for superusers
    const createNewUserCheckbox = document.getElementById('createNewUser')
    if (createNewUserCheckbox) {
        const existingUserSection = document.getElementById('existingUserSection')
        const newUserSection = document.getElementById('newUserSection')
        const createNewUserField = document.getElementById('createNewUserField')
        const existingUserSelect = document.getElementById('id_user')
        const newUserFields = newUserSection.querySelectorAll('input[required]')

        createNewUserCheckbox.addEventListener('change', function () {
            if (this.checked) {
                existingUserSection.classList.add('d-none')
                newUserSection.classList.remove('d-none')
                createNewUserField.value = 'true'

                // Disable existing user select when creating new user
                existingUserSelect.disabled = true

                // Enable validation on new user fields
                newUserFields.forEach((field) => {
                    field.required = true
                })
            } else {
                existingUserSection.classList.remove('d-none')
                newUserSection.classList.add('d-none')
                createNewUserField.value = 'false'

                // Re-enable existing user select
                existingUserSelect.disabled = false

                // Disable validation on new user fields
                newUserFields.forEach((field) => {
                    field.required = false
                })
            }
        })

        // Password confirmation validation
        const password1 = document.getElementById('id_password1')
        const password2 = document.getElementById('id_password2')
        const passwordFeedback = document.getElementById('password-match-feedback')

        function validatePassword() {
            if (password1.value !== password2.value) {
                password2.setCustomValidity("Passwords don't match")
                passwordFeedback.textContent = "Passwords don't match"
                passwordFeedback.style.display = 'block'
            } else {
                password2.setCustomValidity('')
                passwordFeedback.style.display = 'none'
            }
        }

        password1.addEventListener('change', validatePassword)
        password2.addEventListener('keyup', validatePassword)
    }
})
