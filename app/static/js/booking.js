const loadCalendar = () => {
  const datesList = [];

  const today = new Date();
  const beginningTodaysWeek = new Date();
  beginningTodaysWeek.setDate(today.getDate() - today.getDay());
  const beginningFourWeeksAgo = new Date();
  beginningFourWeeksAgo.setDate(beginningTodaysWeek.getDate() - 5 * 7);
  const endingLastWeek = new Date();
  endingLastWeek.setDate(beginningTodaysWeek.getDate() + 52 * 7 + 6);
  const workingDate = new Date(beginningFourWeeksAgo);

  const grid = document.getElementById("calendar-grid");
  grid.innerHTML = "";

  if (grid)
    for (let i = 0; i < 52 * 7 + 6 + 5 * 7; i++) {
      // Create the day div
      const dayDiv = document.createElement("div");
      dayDiv.style.gridRow = `${1 + Math.floor(i / 7)}`;
      dayDiv.style.gridColumn = `${2 + (i % 7)}`;
      dayDiv.classList.add("grid-day");
      if (workingDate.getTime() <= today.getTime())
        dayDiv.classList.add("past");
      if (workingDate.toDateString() == today.toDateString())
        dayDiv.setAttribute("data-day", "today");
      dayDiv.innerText = `${workingDate.getDate()}`;

      // Calculate the start and end of the current week
      const weekStart = new Date(workingDate);
      const weekEnd = new Date(workingDate);
      weekStart.setDate(workingDate.getDate() - workingDate.getDay());
      weekEnd.setDate(workingDate.getDate() - workingDate.getDay() + 6);

      // Determine if the current week is the beginning of the month
      const beginningWeekOfMonth = workingDate.getDate() === 1;
      if (beginningWeekOfMonth) {
        const firstOfNextMonth = new Date(workingDate);
        firstOfNextMonth.setMonth(firstOfNextMonth.getMonth() + 1, 1); // Move to the first day of the next month

        const lastFullWeekEnd = new Date(firstOfNextMonth);
        lastFullWeekEnd.setDate(
          firstOfNextMonth.getDate() - firstOfNextMonth.getDay() - 1
        ); // Calculate the last full week's end date

        const numDaysIncl = Math.round(
          (lastFullWeekEnd.getTime() -
            weekStart.getTime() +
            1000 * 60 * 60 * 24) /
            (1000 * 60 * 60 * 24)
        );

        const numWeeks = Math.floor(numDaysIncl / 7); // Number of weeks to cover

        // Create and append the month label
        const monthDiv = document.createElement("div");
        monthDiv.style.gridRow = `${1 + Math.floor(i / 7)} / ${
          1 + Math.floor(i / 7) + numWeeks
        }`;
        monthDiv.style.gridColumn = "1";
        monthDiv.classList.add("month-label");
        monthDiv.setAttribute("data-year", `${weekEnd.getFullYear()}`);
        monthDiv.innerText = weekEnd.toLocaleString("default", {
          month: "short",
        });

        grid.appendChild(monthDiv);
      }

      // Append the day div to the grid
      grid.appendChild(dayDiv);
      datesList.push({ date: new Date(workingDate), element: dayDiv });
      // Move to the next day
      workingDate.setDate(workingDate.getDate() + 1);
    }
  return datesList;
};

const loadAvailability = async (datesList) => {
  let calendarData = [];

  const calendarAndDayDivs = [];

  // Fetch calendar data from the backend API
  await fetch("/api/available_dates")
    .then((response) => response.json())
    .then((data) => {
      calendarData = data;
      console.log(calendarData);
    })
    .catch((error) => console.error("Error fetching available dates:", error));

  // Iterate over the calendarData and match it with datesList
  calendarData.forEach((calendarEntry, index) => {
    // Convert the calendar entry date (which is a string) back into a Date object
    const entryDate = new Date(
      calendarEntry.year,
      calendarEntry.month - 1,
      calendarEntry.day
    );

    // Check if there is a matching date in datesList
    const matchingDate = datesList.find((dateObj) => {
      return (
        entryDate.getTime() > Date.now() &&
        dateObj.date.getFullYear() === entryDate.getFullYear() &&
        dateObj.date.getMonth() === entryDate.getMonth() &&
        dateObj.date.getDate() === entryDate.getDate()
      );
    });

    // If a matching date is found, add the class .available to the corresponding element
    if (matchingDate) {
      const dayElement = matchingDate.element;

      // Add availability indicators (dot) and set the date as selectable
      dayElement.classList.add("available");
      dayElement.id = `day-${index}`;
      const dot = document.createElement("div");
      dot.className = "dot";
      dayElement.appendChild(dot);
      dayElement.setAttribute("data-selectable", "");

      // Set up the timeslot structure
      const timeslots = {};
      //   morning: false,  // Default to false, assuming unavailable
      //   afternoon: false,
      //   evening: false,
      // };

      // Populate available timeslots based on the API response
      if (calendarEntry.time_slots.morning)
        timeslots.morning = calendarEntry.time_slots.morning;

      if (calendarEntry.time_slots.afternoon)
        timeslots.afternoon = calendarEntry.time_slots.afternoon;

      if (calendarEntry.time_slots.evening)
        timeslots.evening = calendarEntry.time_slots.evening;

      // Add the structured date and timeslot data to the array
      calendarAndDayDivs.push({
        // element: dayElement, // The day HTML element
        date: entryDate, // The actual date object
        id: `day-${index}`, // The unique ID for this date from the backend
        timeslots: timeslots, // The timeslot data (morning, afternoon, evening)
      });
    }
  });
  return calendarAndDayDivs;
};

const setupTimeslotCards = (calendarAndDayDivs) => {
  const timeslotDivs = {
    morning: document.getElementById("morning-timeslot"),
    afternoon: document.getElementById("afternoon-timeslot"),
    evening: document.getElementById("evening-timeslot"),
  };

  const selectionListener = (timeslot, elementsToGray) => {
    return () => {
      // If the timeslot is already selected, deselect it
      calendarAndDayDivs.forEach((cadd) =>
        document.getElementById(cadd.id).classList.remove("disabled")
      );
      if (timeslot.classList.contains("selected")) {
        timeslot.classList.remove("selected");
      } else {
        // Deselect any other selected timeslots-
        timeslotDivs.morning?.classList.remove("selected");
        timeslotDivs.afternoon?.classList.remove("selected");
        timeslotDivs.evening?.classList.remove("selected");

        // Select the clicked timeslot
        timeslot.classList.add("selected");
        elementsToGray.forEach((element) => element.classList.add("disabled"));
      }
    };
  };

  timeslotDivs.morning?.addEventListener(
    "click",
    selectionListener(
      timeslotDivs.morning,
      calendarAndDayDivs
        .filter((cadd) => !cadd.timeslots.morning)
        .map((cadd) => document.getElementById(cadd.id))
    )
  );
  timeslotDivs.afternoon?.addEventListener(
    "click",
    selectionListener(
      timeslotDivs.afternoon,
      calendarAndDayDivs
        .filter((cadd) => !cadd.timeslots.afternoon)
        .map((cadd) => document.getElementById(cadd.id))
    )
  );
  timeslotDivs.evening?.addEventListener(
    "click",
    selectionListener(
      timeslotDivs.evening,
      calendarAndDayDivs
        .filter((cadd) => !cadd.timeslots.evening)
        .map((cadd) => document.getElementById(cadd.id))
    )
  );

  return timeslotDivs;
};

const addAvailabilityFunctionality = (calendarAndDayDivs, timeslots) => {
  const availableDays = document.getElementsByClassName("grid-day available");

  for (const cadd of calendarAndDayDivs) {
    //.forEach((availableDay) => {
    const availableDay = document.getElementById(cadd.id);
    availableDay.addEventListener("click", function () {
      timeslots.morning?.classList.remove("disabled");
      timeslots.afternoon?.classList.remove("disabled");
      timeslots.evening?.classList.remove("disabled");
      // If the card is already selected, deselect it
      if (!cadd.timeslots.morning) timeslots.morning?.classList.add("disabled");
      if (!cadd.timeslots.afternoon)
        timeslots.afternoon?.classList.add("disabled");
      if (!cadd.timeslots.evening) timeslots.evening?.classList.add("disabled");

      if (availableDay.classList.contains("selected")) {
        availableDay.classList.remove("selected");
        timeslots.morning?.classList.remove("disabled");
        timeslots.afternoon?.classList.remove("disabled");
        timeslots.evening?.classList.remove("disabled");
      } else {
        // Deselect any other selected cards
        for (const a of availableDays) {
          a.classList.remove("selected");
        }
        // Select the clicked card
        availableDay.classList.add("selected");
      }
    });
  }
};

const initailizeYearObserver = () => {
  // Maintain a map of currently visible elements
  const visibleElements = new Map();
  const yearName = document.getElementById("calendar-year-name");
  yearName.innerHTML = "";
  const calendarContainer = document.getElementById(
    "calendar-scroll-container"
  );
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        const monthLabel = entry.target;
        const rect = entry.boundingClientRect;

        // If the element is intersecting, add/update it in the map
        if (entry.isIntersecting) {
          visibleElements.set(monthLabel, rect.top);
        } else {
          // Remove elements that are no longer intersecting
          visibleElements.delete(monthLabel);
        }
      });

      // Find the topmost visible element
      if (visibleElements.size > 0) {
        let topmostElement = visibleElements.get(0);
        let minTop = Infinity;

        visibleElements.forEach((top, element) => {
          if (top < minTop) {
            minTop = top;
            topmostElement = element;
          }
        });

        // Update the year label with the year of the topmost visible month
        if (yearName && topmostElement) {
          const year = topmostElement.getAttribute("data-year") || "";
          yearName.textContent = year;
        }
      }
    },
    {
      root: calendarContainer, // Make sure to set this to the actual scrollable container
      threshold: 0, // Trigger as soon as any part of the label enters the view
      rootMargin: "0px", // Adjust root margin if needed
    }
  );

  // Observe all month labels
  document.querySelectorAll(".month-label").forEach((monthLabel) => {
    observer.observe(monthLabel);
  });
};

function scrollToToday() {
  // Find the 'today' element by its data-day attribute
  const todayElement = document.querySelector(
    '#calendar-grid [data-day="today"]'
  );

  if (todayElement) {
    // Get the calendar grid container
    const calendarScrollContainer = document.getElementById(
      "calendar-scroll-container"
    );

    // Calculate the position of the 'today' element relative to the calendar grid container
    const calendarGrid = document.getElementById("calendar-grid");
    const todayRect = todayElement.getBoundingClientRect();

    if (calendarGrid && calendarScrollContainer) {
      const gridRect = calendarGrid.getBoundingClientRect();

      // Compute the scroll position needed to bring the 'today' element into view
      const scrollTop =
        todayRect.top - gridRect.top + calendarScrollContainer.scrollTop;

      // Scroll the calendar container to the calculated position
      calendarScrollContainer.scrollTo({
        top: scrollTop,
        behavior: "instant", // Optional: Add smooth scrolling for a better user experience
      });
    }
  } else {
    console.warn('No element with data-day="today" found.');
  }
}

const setupConfirmButton = (calendarAndDayDivs, timeslots) => {
  const button = document.getElementById("confirm-booking");

  if (button) {
    button.addEventListener("click", async () => {
      let selectedDay = null;
      // Find the selected day object (store the whole object instead of just the element)
      for (const cadd of calendarAndDayDivs) {
        const availableDay = document.getElementById(cadd.id);
        if (availableDay.classList.contains("selected")) {
          selectedDay = cadd;
          break; // Stop after finding the selected day
        }
      }

      // Find the selected timeslot
      let selectedTimeslot = null;
      if (timeslots.morning.classList.contains("selected")) {
        selectedTimeslot = "morning";
      } else if (timeslots.afternoon.classList.contains("selected")) {
        selectedTimeslot = "afternoon";
      } else if (timeslots.evening.classList.contains("selected")) {
        selectedTimeslot = "evening";
      }

      let selectedPricing = null;
      pricingCards = document.querySelectorAll(".pricing-card");
      for (const pc of pricingCards) {
        if (pc.classList.contains("selected")) {
          selectedPricing = new Number(pc.getAttribute("data-pricing-id"));
          break;
        }
      }

      const inputMessageDiv = document.getElementById("message-input");
      const inputMessage = inputMessageDiv.value;

      if (selectedDay && selectedTimeslot && selectedPricing) {
        // Check if the selected timeslot is available for the selected day
        const timeslotData = selectedDay.timeslots[selectedTimeslot];
        console.log(selectedDay.timeslots);
        if (!timeslotData) {
          // Timeslot is not available or missing ID, log a message and stop further execution
          console.log(
            `The selected timeslot (${selectedTimeslot}) is not available for the selected day.`
          );
          return; // Exit the function to prevent the request
        }

        // Prepare data for the request using the timeslot ID
        const data = {
          timeslot_id: timeslotData, // Use the ID associated with the timeslot
          status: "held",
          pricing_id: selectedPricing,
          message: inputMessage
        };
        
        console.log(`Committing timeslot to hold: ${JSON.stringify(data)}`);

        try {
          // Make the PUT request to the backend API to update the status
          const response = await fetch(`/api/update_timeslot_status`, {
            method: "PUT",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify(data), // Send the timeslot ID and new status
          });

          if (!response.ok) {
            throw new Error(`Error: ${response.statusText}`);
          }

          const result = await response.json();
          console.log("Booking confirmed: ", result);

          const datesList = loadCalendar();

          const calendarAndDayDivs = await loadAvailability(datesList);

          const timeslots = {
            morning: document.getElementById("morning-timeslot"),
            afternoon: document.getElementById("afternoon-timeslot"),
            evening: document.getElementById("evening-timeslot"),
          };

          addAvailabilityFunctionality(calendarAndDayDivs, timeslots);

          initailizeYearObserver();
          timeslots.morning.classList.remove("selected");
          timeslots.afternoon.classList.remove("selected");
          timeslots.evening.classList.remove("selected");

          pricingCards.forEach((card) => card.classList.remove("selected"))

          // Optionally, update the UI to reflect the held status
          // This could eventually redirect the user to a payment screen
          window.location.href = '/payment';
          // document
          //   .getElementById(selectedDay.id)
          //   .querySelector(".dot")
          //   .classList.add("held");
        } catch (error) {
          console.error("Failed to confirm booking:", error);
        }
      } else {
        // Handle cases where no day or no timeslot is selected
        console.error(
          `Please select a ${
            !selectedPricing
              ? "pricing option"
              : !selectedDay
              ? "day"
              : "timeslot"
          }`
        );
      }
    });
  }
};

document.addEventListener("DOMContentLoaded", async () => {
  const datesList = loadCalendar();

  const calendarAndDayDivs = await loadAvailability(datesList);

  const timeslots = setupTimeslotCards(calendarAndDayDivs);

  addAvailabilityFunctionality(calendarAndDayDivs, timeslots);

  initailizeYearObserver();

  scrollToToday();

  setupConfirmButton(calendarAndDayDivs, timeslots);
});
