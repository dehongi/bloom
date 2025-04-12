document.addEventListener('DOMContentLoaded', function () {
    const cartItems = document.querySelectorAll('.cart-item')
    const updateUrl = document.getElementById('cart-data').dataset.updateUrl
    const removeUrl = document.getElementById('cart-data').dataset.removeUrl
    const csrfToken = document.getElementById('cart-data').dataset.csrfToken

    // Function to update the cart totals
    function updateCartTotals(subtotal) {
        document.querySelector('.cart-subtotal').textContent = '$' + subtotal
        document.querySelector('.cart-total').textContent = '$' + subtotal
    }

    // Handle quantity changes
    cartItems.forEach((item) => {
        const itemId = item.getAttribute('data-item-id')
        const quantityInput = item.querySelector('.item-quantity')
        const decreaseBtn = item.querySelector('.decrease-quantity')
        const increaseBtn = item.querySelector('.increase-quantity')
        const removeBtn = item.querySelector('.remove-item')
        const subtotalEl = item.querySelector('.item-subtotal')

        // Decrease quantity
        decreaseBtn.addEventListener('click', function () {
            let value = parseInt(quantityInput.value)
            if (value > 1) {
                quantityInput.value = value - 1
                updateItemQuantity(itemId, value - 1)
            }
        })

        // Increase quantity
        increaseBtn.addEventListener('click', function () {
            let value = parseInt(quantityInput.value)
            let max = parseInt(quantityInput.getAttribute('max'))
            if (value < max) {
                quantityInput.value = value + 1
                updateItemQuantity(itemId, value + 1)
            }
        })

        // Input change
        quantityInput.addEventListener('change', function () {
            let value = parseInt(this.value)
            let min = parseInt(this.getAttribute('min'))
            let max = parseInt(this.getAttribute('max'))

            if (value < min) {
                this.value = min
                value = min
            } else if (value > max) {
                this.value = max
                value = max
            }

            updateItemQuantity(itemId, value)
        })

        // Remove item
        removeBtn.addEventListener('click', function () {
            if (confirm('Are you sure you want to remove this item from your cart?')) {
                removeItem(itemId)
            }
        })

        // Update item quantity via AJAX
        function updateItemQuantity(itemId, quantity) {
            const formData = new FormData()
            formData.append('item_id', itemId)
            formData.append('quantity', quantity)
            formData.append('csrfmiddlewaretoken', csrfToken)

            fetch(updateUrl, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
                .then((response) => response.json())
                .then((data) => {
                    if (data.status === 'success') {
                        // Update item subtotal
                        subtotalEl.textContent = '$' + data.item_subtotal

                        // Update cart totals
                        updateCartTotals(data.cart_total)

                        // Update cart count in the header
                        const cartCount = document.querySelector('.cart-count')
                        if (cartCount) {
                            cartCount.textContent = data.cart_count
                        }
                    } else {
                        alert(data.message || 'Error updating cart')
                    }
                })
                .catch((error) => {
                    console.error('Error:', error)
                })
        }

        // Remove item via AJAX
        function removeItem(itemId) {
            const formData = new FormData()
            formData.append('item_id', itemId)
            formData.append('csrfmiddlewaretoken', csrfToken)

            fetch(removeUrl, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
                .then((response) => response.json())
                .then((data) => {
                    if (data.status === 'success') {
                        // Remove the item from the DOM
                        item.remove()

                        // Update cart totals
                        updateCartTotals(data.cart_total)

                        // Update cart count in the header
                        const cartCount = document.querySelector('.cart-count')
                        if (cartCount) {
                            cartCount.textContent = data.cart_count
                        }

                        // Reload the page if no items left
                        if (data.cart_count === 0) {
                            location.reload()
                        }
                    } else {
                        alert(data.message || 'Error removing item')
                    }
                })
                .catch((error) => {
                    console.error('Error:', error)
                })
        }
    })
})
