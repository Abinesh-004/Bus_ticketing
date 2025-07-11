// API helper functions for the bus ticketing system

const API_BASE_URL = '/api/';

// Fetch popular routes
async function getPopularRoutes() {
    try {
        const response = await fetch(`${API_BASE_URL}routes/popular/`);
        return await response.json();
    } catch (error) {
        console.error('Error fetching popular routes:', error);
        return [];
    }
}

// Search buses
async function searchBuses(origin, destination, date) {
    try {
        const response = await fetch(`${API_BASE_URL}buses/search/?origin=${encodeURIComponent(origin)}&destination=${encodeURIComponent(destination)}&date=${date}`);
        return await response.json();
    } catch (error) {
        console.error('Error searching buses:', error);
        return [];
    }
}

// Create booking
async function createBooking(bookingData) {
    try {
        const response = await fetch(`${API_BASE_URL}bookings/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify(bookingData),
        });
        return await response.json();
    } catch (error) {
        console.error('Error creating booking:', error);
        return { error: 'Failed to create booking' };
    }
}

// Helper function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}