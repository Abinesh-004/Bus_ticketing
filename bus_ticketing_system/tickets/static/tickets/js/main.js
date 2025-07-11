// Main JavaScript for the bus ticketing system

// Function to initialize datepicker for search form
function initDatePicker() {
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    
    document.getElementById('id_date').min = today.toISOString().split('T')[0];
}

// Function to handle AJAX calls for seat availability
async function checkSeatAvailability(scheduleId) {
    try {
        const response = await fetch(`/api/seats/${scheduleId}/`);
        const data = await response.json();
        return data.available_seats;
    } catch (error) {
        console.error('Error checking seat availability:', error);
        return 0;
    }
}

// Initialize functions when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initDatePicker();
    
    // Add any other initialization code here
});

// Toast notification function
function showToast(message, type = 'success') {
    const toastContainer = document.createElement('div');
    toastContainer.className = `toast align-items-center text-white bg-${type} border-0`;
    toastContainer.setAttribute('role', 'alert');
    toastContainer.setAttribute('aria-live', 'assertive');
    toastContainer.setAttribute('aria-atomic', 'true');
    
    toastContainer.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    document.body.appendChild(toastContainer);
    const toast = new bootstrap.Toast(toastContainer);
    toast.show();
    
    // Remove toast after it's hidden
    toastContainer.addEventListener('hidden.bs.toast', function() {
        document.body.removeChild(toastContainer);
    });
}