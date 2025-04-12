document.addEventListener('DOMContentLoaded', function () {
    // Handle add to cart button clicks
    const addToCartButtons = document.querySelectorAll('.add-to-cart')
    addToCartButtons.forEach((button) => {
        button.addEventListener('click', function (e) {
            e.preventDefault()
            const productId = this.getAttribute('data-product-id')
            const url = this.getAttribute('data-url')
            const csrfToken = document.getElementById('product-list-data').getAttribute('data-csrf-token')

            // Create form data
            const formData = new FormData()
            formData.append('product_id', productId)
            formData.append('quantity', 1)
            formData.append('csrfmiddlewaretoken', csrfToken)

            // Send AJAX request
            fetch(url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
                .then((response) => response.json())
                .then((data) => {
                    if (data.status === 'success') {
                        // Update cart count
                        const cartCount = document.querySelector('.cart-count')
                        if (cartCount) {
                            cartCount.textContent = data.cart_count
                        }

                        // Show success message
                        alert(data.message)
                    } else {
                        // Show error message
                        alert(data.message || 'Error adding to cart')
                    }
                })
                .catch((error) => {
                    console.error('Error:', error)
                    alert('An error occurred while adding to cart')
                })
        })
    })

    // Handle sort change
    const sortSelect = document.getElementById('sort')
    if (sortSelect) {
        sortSelect.addEventListener('change', function () {
            document.querySelector('form').submit()
        })
    }
})
