document.addEventListener("DOMContentLoaded", () => {

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
      threshold: [...Array(30).keys()].map((k) => k / 30.0), 
    }
  );

  // Select all elements with .swiper-coverup class and observe them
  const swiperCoverups = document.querySelectorAll(".swiper-coverup");
  swiperCoverups.forEach((div) => observer.observe(div));
});
