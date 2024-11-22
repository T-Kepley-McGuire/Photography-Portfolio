function redistributeColumns() {
  const container = document.getElementById("portfolio-container");

  const numCols = getNumberOfColumns();

  const allColumns = document.getElementsByClassName("grid-column");
  // console.log(allColumns);
  const currentlyShown = [];
  for (let i = 0; i < allColumns.length; i++) {
    // columns.push(allColumns[i]);
    allColumns[i].classList.remove("shown");
    if (i < numCols) {
      allColumns[i].classList.add("shown");
      currentlyShown.push(allColumns[i]);
    }
    // allColumns[i].style.display = i < numCols ? "flex" : "none";
  }

  return currentlyShown;
}

imageElements = [];

let previousNumCols = 0;
document.addEventListener("DOMContentLoaded", async () => {
  imageUrls = await fetch("/portfolio/images").then((response) =>
    response.json()
  );
  imageUrls = imageUrls.map((e, i) => {
    return { url: e, index: i };
  });

  const arrow = document.getElementById("look-down-arrow");
  let arrowVisible = true;
  redistributeColumns();
  previousNumCols = getNumberOfColumns();
  // Create the observer
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting && imageUrls.length > 0) {
          if (arrowVisible) {
            arrow.style.opacity = "0";
            arrowVisible = false;
          }
          const newImage = document.createElement("img");
          newImage.classList.add("photothumb");
          newImage.alt = `Image ${imageUrls[0].index}`;
          newImage.src = imageUrls[0].url;
          imageUrls.splice(0, 1);

          // if (imageUrls.length === 0) {
          //   entries.forEach((e) => e.target.classList.add("shorten"));
          // }

          newImage.onload = function () {
            newImage.style.opacity = "1";
          };
          imageElements.push(newImage);
          entry.target.before(newImage);
        }
      });
    },
    { threshold: 0.5 }
  );

  // Select all elements with .swiper-coverup class and observe them
  const bots = document.querySelectorAll(".bottom-observer");
  bots.forEach((b) => observer.observe(b));
});

// Function to get the number of columns in the grid
function getNumberOfColumns() {
  const grid = document.querySelector(".grid");
  const computedStyle = window.getComputedStyle(grid);
  const columns = computedStyle.getPropertyValue("grid-template-columns");
  return columns.split(" ").length; // returns the number of columns
}

// Function to calculate the height of a column
function getColumnHeight(column) {
  return column.lastChild.offsetTop;
  // const rect = observer.getBoundingClientRect(); // Get position relative to viewport
  // const scrollTop = window.scrollY || document.documentElement.scrollTop;
  // return rect.top + scrollTop; // Absolute position relative to the document

}

// Function to redistribute images based on the height of each column
function redistributeImagesByHeight() {

  const grid = document.querySelector(".grid");

  // Get all the old columns
  const oldColumns = Array.from(grid.children);

  // Collect all images from the old columns (excluding the last child of each column)
  const allImages = [];

  oldColumns.forEach((column) => {
    const images = Array.from(column.children).slice(0, -1); // Exclude last child
    images.forEach((img) => column.removeChild(img));
    allImages.push(...images); // Flatten the images into one list
  });

  

  console.log(allImages);

  const numCols = getNumberOfColumns();
  const newColumns = oldColumns.filter((_, i) => i < numCols);

  // Clear all columns
  // oldColumns.forEach((column) => (column.innerHTML = ""));

  // Track column heights
  const lastChildren = newColumns.map((col) => col.lastChild);
  const columnHeights = newColumns.map(getColumnHeight);
  console.log(columnHeights)
  // Redistribute the images based on column height
  allImages.forEach((img) => {
    // Find the index of the column with the smallest height
    let smallestColumnIndex = columnHeights.indexOf(Math.min(...columnHeights));

    // Append the image to that column
    lastChildren[smallestColumnIndex].before(img);

    // Update the height of that column after adding the image
    columnHeights[smallestColumnIndex] = getColumnHeight(
      newColumns[smallestColumnIndex]
    );
    console.log(columnHeights)
  });
}

window.addEventListener("resize", () => {
  if (previousNumCols != getNumberOfColumns()) {
    redistributeColumns();
    redistributeImagesByHeight();
    previousNumCols = getNumberOfColumns();
  }
});

// Debounce the resize event to avoid excessive recalculations
// let resizeTimeout;
// window.addEventListener('resize', function () {
//   clearTimeout(resizeTimeout);
//   resizeTimeout = setTimeout(() => {
//     redistributeImagesByHeight();
//   }, 100); // 100ms delay to debounce
// });
