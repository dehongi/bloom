document.addEventListener('DOMContentLoaded', function () {
    // Get data from the checkout-data element
    const checkoutData = document.getElementById('checkout-data');
    const subtotal = parseFloat(checkoutData.getAttribute('data-subtotal'));
    const discountAmount = parseFloat(checkoutData.getAttribute('data-discount-amount') || 0);
    const csrfToken = checkoutData.getAttribute('data-csrf-token');
    const orderSuccessUrl = checkoutData.getAttribute('data-order-success-url');

    // Toggle billing address form
    const sameAsShippingCheckbox = document.getElementById('same_as_shipping');
    const billingAddressForm = document.getElementById('billing-address-form');

    sameAsShippingCheckbox.addEventListener('change', function () {
        if (this.checked) {
            billingAddressForm.style.display = 'none';
            // Clear required attributes when hidden
            document.querySelectorAll('#billing-address-form input, #billing-address-form select').forEach(input => {
                input.required = false;
            });
        } else {
            billingAddressForm.style.display = 'block';
            // Add required attributes when visible
            document.querySelectorAll('#billing-address-form input, #billing-address-form select').forEach(input => {
                if (input.id !== 'id_billing_address2') {
                    input.required = true;
                }
            });
        }
    });

    // Toggle payment method forms
    const paymentMethodRadios = document.querySelectorAll('input[name="payment_method"]');
    const creditCardForm = document.getElementById('credit-card-form');
    const paypalForm = document.getElementById('paypal-form');

    paymentMethodRadios.forEach(radio => {
        radio.addEventListener('change', function () {
            if (this.value === 'credit') {
                creditCardForm.style.display = 'block';
                paypalForm.style.display = 'none';
                // Add required attributes to credit card fields
                document.querySelectorAll('#credit-card-form input').forEach(input => {
                    input.required = true;
                });
            } else if (this.value === 'paypal') {
                creditCardForm.style.display = 'none';
                paypalForm.style.display = 'block';
                // Remove required attributes from credit card fields
                document.querySelectorAll('#credit-card-form input').forEach(input => {
                    input.required = false;
                });
            }
        });
    });

    // Calculate shipping and taxes
    const shippingCountry = document.getElementById('id_shipping_country');
    const shippingState = document.getElementById('id_shipping_state');
    const shippingCost = document.getElementById('shipping-cost');
    const taxAmount = document.getElementById('tax-amount');
    const orderTotal = document.getElementById('order-total');

    function updateTotals() {
        const country = shippingCountry.value;
        let shipping = 0;
        let tax = 0;

        // Simple logic for demonstration - replace with actual calculation
        if (country === 'US') {
            shipping = 5.99;
            tax = subtotal * 0.07; // 7% tax rate for US
        } else if (country === 'CA') {
            shipping = 9.99;
            tax = subtotal * 0.13; // 13% tax rate for Canada
        } else if (country === 'UK') {
            shipping = 14.99;
            tax = subtotal * 0.20; // 20% VAT for UK
        }

        shippingCost.textContent = '$' + shipping.toFixed(2);
        taxAmount.textContent = '$' + tax.toFixed(2);

        const total = subtotal + shipping + tax - discountAmount;
        orderTotal.textContent = '$' + total.toFixed(2);

        // Add hidden fields for form submission
        document.getElementById('id_shipping_cost').value = shipping.toFixed(2);
        document.getElementById('id_tax_amount').value = tax.toFixed(2);
        document.getElementById('id_total_amount').value = total.toFixed(2);
    }

    // Call updateTotals on initial load
    updateTotals();

    shippingCountry.addEventListener('change', updateTotals);
    shippingState.addEventListener('change', updateTotals);

    // Apply coupon
    const couponInput = document.getElementById('id_coupon');
    const applyCouponButton = document.getElementById('apply-coupon');

    applyCouponButton.addEventListener('click', function () {
        const couponCode = couponInput.value.trim();

        if (couponCode) {
            // This would normally be an AJAX call to validate the coupon
            fetch('/shop/apply-coupon/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    coupon_code: couponCode
                })
            })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        alert('Coupon applied successfully!');
                        // Update totals based on coupon discount
                        updateTotals();
                    } else {
                        alert(data.message || 'Invalid coupon code');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Error applying coupon');
                });
        } else {
            alert('Please enter a coupon code');
        }
    });

    // Form validation
    const checkoutForm = document.getElementById('checkoutForm');

    checkoutForm.addEventListener('submit', function (event) {
        event.preventDefault();

        // This would normally validate the form and submit it
        alert('Order placed successfully! This is just a demo. In a real application, this would submit the order and redirect to a confirmation page.');

        // Redirect to a confirmation page
        // window.location.href = orderSuccessUrl;
    });
});
