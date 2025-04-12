// Simple script to filter employees based on role
document.addEventListener('DOMContentLoaded', function () {
    const roleSelector = document.querySelector('.role-selector')
    const employeeSelect = document.getElementById('id_employee')

    if (roleSelector && employeeSelect) {
        roleSelector.addEventListener('change', function () {
            const selectedRole = this.value

            // Get the right filter attribute based on role
            let filterAttribute = ''
            if (selectedRole === 'designer') {
                filterAttribute = this.getAttribute('data-designer-filter')
            } else if (selectedRole === 'delivery') {
                filterAttribute = this.getAttribute('data-delivery-filter')
            } else if (selectedRole === 'manager' || selectedRole === 'sales') {
                filterAttribute = this.getAttribute('data-processor-filter')
            }

            // Make AJAX request to get filtered employees
            // This is a placeholder - in a real implementation you would fetch from the server
            // For now we'll just add a helper message
            document.getElementById('employee-filter-help').textContent = `Showing employees with ${filterAttribute} capability`
        })
    }
})
