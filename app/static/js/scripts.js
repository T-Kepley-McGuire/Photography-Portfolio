// Initialize Calendar (using a library like FullCalendar)
document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');

    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        dateClick: function(info) {
            openTimeModal(info.dateStr);
        },
        events: function(fetchInfo, successCallback, failureCallback) {
            fetch('http://127.0.0.1:5000/available-dates')
                .then(response => response.json())
                .then(data => {
                    successCallback(data);
                })
                .catch(error => {
                    failureCallback(error);
                });
        }
    });

    calendar.render();
});

// Open the time modal and fetch available time slots
function openTimeModal(date) {
    document.getElementById('timeModal').style.display = 'block';

    fetch(`http://127.0.0.1:5000/available-times?date=${date}`)
        .then(response => response.json())
        .then(data => {
            displayTimeSlots(data, date);
        })
        .catch(error => {
            console.error('Error fetching time slots:', error);
        });
}

// Display time slots in the modal
function displayTimeSlots(slots, date) {
    const timeSlotsDiv = document.getElementById('timeSlots');
    timeSlotsDiv.innerHTML = ''; // Clear previous time slots

    slots.forEach(slot => {
        const button = document.createElement('button');
        button.textContent = slot;
        button.addEventListener('click', function() {
            handleTimeSelection(slot, date);
        });
        timeSlotsDiv.appendChild(button);
    });
}

function handleTimeSelection(time, date) {
    fetch('http://127.0.0.1:5000/hold-time-slot', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            date: date,
            time: time
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Successfully held the time slot, store in localStorage and proceed
            localStorage.setItem('selectedTime', time);
            localStorage.setItem('selectedDate', date);
            localStorage.setItem('holdId', data.holdId); // Store the hold ID to check later
            window.location.href = 'pricing.html';
        } else {
            alert('The selected time slot is no longer available. Please choose another.');
        }
    })
    .catch(error => {
        console.error('Error holding time slot:', error);
        alert('An error occurred. Please try again.');
    });
}


// Close the modal
document.querySelector('.close').onclick = function() {
    document.getElementById('timeModal').style.display = 'none';
};

// Close the modal if user clicks outside of it
window.onclick = function(event) {
    if (event.target == document.getElementById('timeModal')) {
        document.getElementById('timeModal').style.display = 'none';
    }
};

// On the pricing page, fetch pricing information
document.addEventListener('DOMContentLoaded', function() {
    if (window.location.pathname.endsWith('pricing.html')) {
        fetch('http://127.0.0.1:5000/pricing-options')
            .then(response => response.json())
            .then(data => {
                displayPricingOptions(data);
            })
            .catch(error => {
                console.error('Error fetching pricing options:', error);
            });
    }
});

function displayPricingOptions(options) {
    const section = document.querySelector('.pricing ul');
    section.innerHTML = ''; // Clear previous options

    options.forEach(option => {
        const li = document.createElement('li');
        li.innerHTML = `<strong>${option.name}:</strong> ${option.description} - ${option.price}`;
        section.appendChild(li);
    });

    // Add a "Book Now" button
    const button = document.createElement('button');
    button.textContent = 'Book Now';
    button.addEventListener('click', handleBooking);
    section.appendChild(button);
}

function handleBooking() {
    const selectedDate = localStorage.getItem('selectedDate');
    const selectedTime = localStorage.getItem('selectedTime');
    const holdId = localStorage.getItem('holdId'); // Get the hold ID

    // Verify the hold before proceeding
    fetch(`http://127.0.0.1:5000/verify-hold?holdId=${holdId}`)
        .then(response => response.json())
        .then(data => {
            if (data.valid) {
                // Proceed with the booking since the hold is valid
                fetch('http://127.0.0.1:5000/book-session', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        date: selectedDate,
                        time: selectedTime,
                        package: selectedPackage,
                        paymentStatus: "Paid"
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        window.location.href = 'success.html';
                    } else {
                        alert('Booking failed. Please try again.');
                    }
                })
                .catch(error => {
                    console.error('Error booking session:', error);
                    alert('An error occurred. Please try again.');
                });
            } else {
                alert('The hold on your selected time slot has expired or is no longer valid. Please choose another time.');
                // Redirect to the time selection page or refresh
                window.location.href = 'pricing.html';
            }
        })
        .catch(error => {
            console.error('Error verifying hold:', error);
            alert('An error occurred. Please try again.');
        });
}

// Periodic check every 2 minutes
const holdVerificationInterval = setInterval(() => {
    const holdId = localStorage.getItem('holdId');
    
    fetch(`http://127.0.0.1:5000/verify-hold?holdId=${holdId}`)
        .then(response => response.json())
        .then(data => {
            if (!data.valid) {
                alert('The hold on your selected time slot has expired. Please select another time.');
                clearInterval(holdVerificationInterval);
                window.location.href = 'booking.html'; // Redirect to re-select time slot
            }
        })
        .catch(error => {
            console.error('Error verifying hold:', error);
        });
}, 120000); // 120000 milliseconds = 2 minutes


