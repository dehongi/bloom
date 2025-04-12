document.addEventListener('DOMContentLoaded', function () {
    // Product image gallery
    const thumbnails = document.querySelectorAll('.product-gallery-thumb')
    const mainImage = document.getElementById('mainProductImage')

    thumbnails.forEach((thumb) => {
        thumb.addEventListener('click', function () {
            // Update main image
            mainImage.src = this.getAttribute('data-img-src')

            // Update active state
            thumbnails.forEach((t) => t.classList.remove('active'))
            this.classList.add('active')
        })
    })

    // Quantity controls
    const quantityInput = document.getElementById('quantity')
    const decreaseBtn = document.getElementById('decreaseQuantity')
    const increaseBtn = document.getElementById('increaseQuantity')

    decreaseBtn.addEventListener('click', function () {
        let value = parseInt(quantityInput.value)
        if (value > 1) {
            quantityInput.value = value - 1
        }
    })

    increaseBtn.addEventListener('click', function () {
        let value = parseInt(quantityInput.value)
        let max = parseInt(quantityInput.getAttribute('max'))
        if (value < max) {
            quantityInput.value = value + 1
        }
    })

    // Review form toggle
    const writeReviewBtn = document.getElementById('writeReviewBtn')
    const cancelReviewBtn = document.getElementById('cancelReviewBtn')
    const reviewForm = document.getElementById('reviewForm')

    if (writeReviewBtn && reviewForm) {
        writeReviewBtn.addEventListener('click', function () {
            reviewForm.classList.add('active')
            writeReviewBtn.style.display = 'none'
        })
    }

    if (cancelReviewBtn && reviewForm && writeReviewBtn) {
        cancelReviewBtn.addEventListener('click', function () {
            reviewForm.classList.remove('active')
            writeReviewBtn.style.display = 'block'
        })
    }

    // Handle variant selection (update price)
    const variantSelect = document.getElementById('variant')
    if (variantSelect) {
        variantSelect.addEventListener('change', function () {
            // TODO: Update price based on variant selection
        })
    }

    // Handle add to cart form submission
    const addToCartForm = document.getElementById('addToCartForm')
    addToCartForm.addEventListener('submit', function (e) {
        e.preventDefault()

        // Create form data
        const formData = new FormData(this)

        // Send AJAX request
        fetch(this.action, {
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
