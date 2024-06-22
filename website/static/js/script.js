document.addEventListener('DOMContentLoaded', function() {
    const carousel = document.querySelector('.carousel');
    let currentIndex = 0;
    const totalImages = document.querySelectorAll('.carousel img').length;
    let visibleImages = getVisibleImages();

    function getVisibleImages() {
        if (window.innerWidth <= 480) {
            return 2; // 2 images at a time for mobile
        } else if (window.innerWidth <= 768) {
            return 3; // 3 images at a time for tablets
        } else {
            return 4; // 4 images at a time for desktop
        }
    }

    function moveCarousel() {
        currentIndex++;
        if (currentIndex >= totalImages - visibleImages + 1) {
            currentIndex = 0;
        }
        const offset = currentIndex * (carousel.querySelector('.custom-img').clientWidth + 10); // Include margin in offset calculation
        carousel.style.transform = `translateX(-${offset}px)`;
    }

    window.addEventListener('resize', () => {
        visibleImages = getVisibleImages();
        currentIndex = 0; // Reset index on resize to prevent out-of-bound errors
        carousel.style.transform = 'translateX(0)'; // Reset carousel position
    });

    setInterval(moveCarousel, 2000); // Adjust speed as needed
});
