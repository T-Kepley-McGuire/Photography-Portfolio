document.addEventListener("DOMContentLoaded", () => {
  console.log([...Array(30).keys()].map((k) => k / 30.0));
  // Function to calculate the opacity based on the closeness to the centerline
  function calculateOpacity(x, m, b) {
    // If within threshold, opacity should gradually reduce
    return Math.min(Math.max(0, m * x + b), 0.8);
  }

  // Create the observer
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        const div = entry.target;

        const newOpacity = (1-entry.intersectionRatio) * 0.8; 
        div.style.backgroundColor = `rgba(0, 0, 0, ${newOpacity})`;
      });
    },
    {
      threshold: [...Array(30).keys()].map((k) => k / 30.0), //[0.1, 0.5, 1], // Adjust this based on how you want to trigger the intersection
    }
  );

  // Select all elements with .swiper-coverup class and observe them
  const swiperCoverups = document.querySelectorAll(".swiper-coverup");
  swiperCoverups.forEach((div) => observer.observe(div));
});
