document.addEventListener('DOMContentLoaded', () => {
    // 1. Category Filtering
    const categories = document.querySelectorAll('.category-item');
    const coupons = document.querySelectorAll('.coupon-card-item');

    categories.forEach(item => {
        item.addEventListener('click', () => {
            // Remove active from all, add to clicked
            categories.forEach(c => c.classList.remove('active'));
            item.classList.add('active');

            const selectedCat = item.getAttribute('data-category');

            coupons.forEach(coupon => {
                const couponCat = coupon.getAttribute('data-category');
                if (selectedCat === 'all' || couponCat === selectedCat) {
                    coupon.style.display = 'block';
                } else {
                    coupon.style.display = 'none';
                }
            });
        });
    });
});

// 2. Buy Functionality Simulation
function handleBuy(brand) {
    alert(`Redirecting to secure payment for ${brand} coupon. Our Escrow system will hold your funds until you verify the code!`);
}

