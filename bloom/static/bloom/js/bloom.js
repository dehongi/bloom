// Bloom App JavaScript

document.addEventListener('DOMContentLoaded', function () {
    // Product selection in order forms - populates fields based on product selection
    const productSelects = document.querySelectorAll('[data-product-select="true"]');

    productSelects.forEach(select => {
        select.addEventListener('change', function () {
            const productId = this.value;
            if (!productId) return;

            const row = this.closest('.form-row') || this.closest('.mb-3').parentNode;

            // Find the name, price, and description fields in the same row
            const nameField = row.querySelector('input[name$="-name"]');
            const priceField = row.querySelector('input[name$="-price"]');
            const descriptionField = row.querySelector('textarea[name$="-description"]');

            // Fetch product info via AJAX
            fetch(`/bloom/api/product-info/?product_id=${productId}`)
                .then(response => response.json())
                .then(data => {
                    if (nameField) nameField.value = data.name;
                    if (priceField) priceField.value = data.price;
                    if (descriptionField) descriptionField.value = data.description;
                })
                .catch(error => console.error('Error fetching product info:', error));
        });
    });

    // Add more item button in order form
    const addItemBtn = document.getElementById('add-item-btn');
    if (addItemBtn) {
        addItemBtn.addEventListener('click', function (e) {
            e.preventDefault();
            const formsetPrefix = this.dataset.formsetPrefix;
            const totalFormsInput = document.getElementById(`id_${formsetPrefix}-TOTAL_FORMS`);

            // Clone the last form
            const forms = document.querySelectorAll(`.${formsetPrefix}-form`);
            const lastForm = forms[forms.length - 1];
            const newForm = lastForm.cloneNode(true);

            // Update form index
            const formCount = forms.length;
            newForm.innerHTML = newForm.innerHTML.replace(
                new RegExp(`${formsetPrefix}-\\d+`, 'g'),
                `${formsetPrefix}-${formCount}`
            );

            // Clear values
            newForm.querySelectorAll('input:not([type="hidden"]), textarea, select').forEach(input => {
                input.value = '';
                if (input.tagName === 'SELECT') {
                    input.selectedIndex = 0;
                }
            });

            // Add the new form
            lastForm.after(newForm);
            totalFormsInput.value = formCount + 1;

            // Re-initialize any event handlers
            newForm.querySelectorAll('[data-product-select="true"]').forEach(select => {
                select.addEventListener('change', function () {
                    // Same product selection handler as above
                    const productId = this.value;
                    if (!productId) return;

                    const row = this.closest('.form-row') || this.closest('.mb-3').parentNode;

                    const nameField = row.querySelector('input[name$="-name"]');
                    const priceField = row.querySelector('input[name$="-price"]');
                    const descriptionField = row.querySelector('textarea[name$="-description"]');

                    fetch(`/bloom/api/product-info/?product_id=${productId}`)
                        .then(response => response.json())
                        .then(data => {
                            if (nameField) nameField.value = data.name;
                            if (priceField) priceField.value = data.price;
                            if (descriptionField) descriptionField.value = data.description;
                        })
                        .catch(error => console.error('Error fetching product info:', error));
                });
            });
        });
    }

    // Delete confirmation
    const deleteButtons = document.querySelectorAll('.delete-confirm-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function (e) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });

    // Order status update form toggle
    const updateStatusBtn = document.getElementById('update-status-btn');
    const statusUpdateForm = document.getElementById('status-update-form');

    if (updateStatusBtn && statusUpdateForm) {
        updateStatusBtn.addEventListener('click', function () {
            statusUpdateForm.classList.toggle('d-none');
        });
    }

    // Customer search autocomplete
    const customerSearchInput = document.getElementById('customer-search');
    if (customerSearchInput) {
        customerSearchInput.addEventListener('input', debounce(function () {
            const searchTerm = this.value.trim();
            if (searchTerm.length < 2) return;

            fetch(`/bloom/api/customer-search/?term=${encodeURIComponent(searchTerm)}`)
                .then(response => response.json())
                .then(data => {
                    const resultsContainer = document.getElementById('customer-search-results');
                    resultsContainer.innerHTML = '';

                    data.forEach(customer => {
                        const item = document.createElement('div');
                        item.className = 'p-2 border-bottom customer-result';
                        item.textContent = customer.name;
                        item.dataset.id = customer.id;

                        item.addEventListener('click', function () {
                            customerSearchInput.value = customer.name;
                            document.getElementById('id_customer').value = customer.id;
                            resultsContainer.innerHTML = '';
                        });

                        resultsContainer.appendChild(item);
                    });

                    if (data.length > 0) {
                        resultsContainer.classList.remove('d-none');
                    } else {
                        resultsContainer.classList.add('d-none');
                    }
                })
                .catch(error => console.error('Error searching customers:', error));
        }, 300));
    }

    // Debounce function for search inputs
    function debounce(func, wait) {
        let timeout;
        return function (...args) {
            const context = this;
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(context, args), wait);
        };
    }

    // Initialize datepickers
    const datepickers = document.querySelectorAll('.datepicker');
    datepickers.forEach(datepicker => {
        // Use browser's native date picker
        datepicker.type = 'date';
    });

    // Calculate order totals on item changes
    function calculateOrderTotal() {
        const subtotalElem = document.getElementById('subtotal-display');
        const discountElem = document.getElementById('discount-display');
        const taxElem = document.getElementById('tax-display');
        const shippingElem = document.getElementById('shipping-display');
        const totalElem = document.getElementById('total-display');

        if (!subtotalElem) return;

        // Calculate subtotal from items
        let subtotal = 0;
        document.querySelectorAll('[data-item-total]').forEach(elem => {
            subtotal += parseFloat(elem.dataset.itemTotal);
        });

        // Get discount percentage and shipping charge
        const discountPercentage = parseFloat(document.getElementById('id_discount_percentage').value || 0);
        const shippingCharge = parseFloat(document.getElementById('id_shipping_charge').value || 0);
        const taxAmount = parseFloat(document.getElementById('id_tax_amount').value || 0);

        // Calculate discount amount
        const discountAmount = (subtotal * discountPercentage) / 100;

        // Calculate total
        const total = subtotal - discountAmount + shippingCharge + taxAmount;

        // Update display
        subtotalElem.textContent = subtotal.toFixed(2);
        if (discountElem) discountElem.textContent = discountAmount.toFixed(2);
        if (taxElem) taxElem.textContent = taxAmount.toFixed(2);
        if (shippingElem) shippingElem.textContent = shippingCharge.toFixed(2);
        totalElem.textContent = total.toFixed(2);

        // Update hidden field for total
        document.getElementById('id_total').value = total.toFixed(2);
        document.getElementById('id_subtotal').value = subtotal.toFixed(2);
        document.getElementById('id_discount_value').value = discountAmount.toFixed(2);
    }

    // Calculate item totals
    function calculateItemTotal(itemRow) {
        const priceInput = itemRow.querySelector('[name$="-price"]');
        const quantityInput = itemRow.querySelector('[name$="-quantity"]');
        const totalSpan = itemRow.querySelector('.item-total');

        if (!priceInput || !quantityInput || !totalSpan) return;

        const price = parseFloat(priceInput.value || 0);
        const quantity = parseInt(quantityInput.value || 0);
        const total = price * quantity;

        totalSpan.textContent = total.toFixed(2);
        totalSpan.dataset.itemTotal = total;

        // Recalculate order total
        calculateOrderTotal();
    }

    // Event listeners for price and quantity inputs
    const orderForm = document.getElementById('order-form');
    if (orderForm) {
        orderForm.addEventListener('input', function (e) {
            if (e.target.name.includes('-price') || e.target.name.includes('-quantity')) {
                const itemRow = e.target.closest('.form-row') || e.target.closest('.mb-3').parentNode;
                calculateItemTotal(itemRow);
            }

            if (e.target.id === 'id_discount_percentage' || e.target.id === 'id_shipping_charge' || e.target.id === 'id_tax_amount') {
                calculateOrderTotal();
            }
        });

        // Calculate initial totals
        document.querySelectorAll('.form-row, .formset-form').forEach(calculateItemTotal);
        calculateOrderTotal();
    }
}); 