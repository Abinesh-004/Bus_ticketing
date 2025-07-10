// Nepal Bus Ticketing System - Main JavaScript File


document.addEventListener('DOMContentLoaded', function() {
  // Initialize all components
  initSeatSelection();
  initFormValidation();
  initSearchForm();
  initBookingSystem();
  initNotifications();
  initDatePicker();
  initMobileMenu();
  initTooltips();
  initPaymentMethods();
  initBusFilters();
  initLoadingStates();
});

// Seat Selection System
let selectedSeats = [];
let seatPrices = {};
let totalAmount = 0;

function initSeatSelection() {
  const seats = document.querySelectorAll('.seat');
  const summaryContainer = document.querySelector('.booking-summary');
  
  seats.forEach(seat => {
      if (seat.classList.contains('available')) {
          seat.addEventListener('click', handleSeatClick);
      }
  });
  
  // Load seat prices from data attributes
  seats.forEach(seat => {
      const seatNumber = seat.dataset.seatNumber;
      const price = parseFloat(seat.dataset.price) || 0;
      seatPrices[seatNumber] = price;
  });
}

function handleSeatClick(event) {
  const seat = event.target;
  const seatNumber = seat.dataset.seatNumber;
  const price = seatPrices[seatNumber];
  
  if (seat.classList.contains('selected')) {
      // Deselect seat
      seat.classList.remove('selected');
      selectedSeats = selectedSeats.filter(s => s !== seatNumber);
      totalAmount -= price;
  } else {
      // Select seat (limit to 4 seats)
      if (selectedSeats.length < 4) {
          seat.classList.add('selected');
          selectedSeats.push(seatNumber);
          totalAmount += price;
      } else {
          showNotification('You can select maximum 4 seats at a time', 'warning');
      }
  }
  
  updateBookingSummary();
  updateSeatCounter();
}

function updateBookingSummary() {
  const summaryBody = document.querySelector('.booking-summary-body');
  const totalElement = document.querySelector('.booking-total');
  
  if (summaryBody) {
      summaryBody.innerHTML = '';
      
      selectedSeats.forEach(seatNumber => {
          const price = seatPrices[seatNumber];
          const item = document.createElement('div');
          item.className = 'summary-item';
          item.innerHTML = `
              <span>Seat ${seatNumber}</span>
              <span>Rs. ${price.toFixed(2)}</span>
          `;
          summaryBody.appendChild(item);
      });
      
      // Add service charge
      const serviceCharge = totalAmount * 0.05; // 5% service charge
      const serviceItem = document.createElement('div');
      serviceItem.className = 'summary-item';
      serviceItem.innerHTML = `
          <span>Service Charge (5%)</span>
          <span>Rs. ${serviceCharge.toFixed(2)}</span>
      `;
      summaryBody.appendChild(serviceItem);
      
      const finalTotal = totalAmount + serviceCharge;
      if (totalElement) {
          totalElement.textContent = `Rs. ${finalTotal.toFixed(2)}`;
      }
  }
}

function updateSeatCounter() {
  const counter = document.querySelector('.seat-counter');
  if (counter) {
      counter.textContent = `${selectedSeats.length} seat(s) selected`;
  }
}

// Form Validation
function initFormValidation() {
  const forms = document.querySelectorAll('.needs-validation');
  
  forms.forEach(form => {
      form.addEventListener('submit', function(event) {
          if (!form.checkValidity()) {
              event.preventDefault();
              event.stopPropagation();
              showValidationErrors(form);
          }
          form.classList.add('was-validated');
      });
  });
}

function showValidationErrors(form) {
  const invalidFields = form.querySelectorAll(':invalid');
  let firstInvalid = null;
  
  invalidFields.forEach(field => {
      if (!firstInvalid) firstInvalid = field;
      
      const errorMessage = field.validationMessage;
      showFieldError(field, errorMessage);
  });
  
  if (firstInvalid) {
      firstInvalid.focus();
  }
}

function showFieldError(field, message) {
  const errorElement = field.parentNode.querySelector('.error-message');
  if (errorElement) {
      errorElement.textContent = message;
      errorElement.style.display = 'block';
  }
}

// Search Form
function initSearchForm() {
  const searchForm = document.querySelector('.search-form');
  const fromCity = document.querySelector('#from-city');
  const toCity = document.querySelector('#to-city');
  const swapButton = document.querySelector('.swap-cities');
  
  if (swapButton) {
      swapButton.addEventListener('click', function() {
          const fromValue = fromCity.value;
          const toValue = toCity.value;
          
          fromCity.value = toValue;
          toCity.value = fromValue;
          
          // Add animation
          swapButton.style.transform = 'rotate(180deg)';
          setTimeout(() => {
              swapButton.style.transform = 'rotate(0deg)';
          }, 300);
      });
  }
  
  // Auto-suggest for cities
  if (fromCity) {
      initCityAutocomplete(fromCity);
  }
  if (toCity) {
      initCityAutocomplete(toCity);
  }
}

function initCityAutocomplete(input) {
  const cities = [
      'Kathmandu', 'Pokhara', 'Chitwan', 'Lumbini', 'Biratnagar',
      'Dharan', 'Hetauda', 'Butwal', 'Nepalgunj', 'Dhangadhi',
      'Janakpur', 'Ilam', 'Gorkha', 'Bandipur', 'Nagarkot',
      'Bharatpur', 'Birgunj', 'Tansen', 'Dhulikhel', 'Bhaktapur'
  ];
  
  let currentFocus = -1;
  
  input.addEventListener('input', function() {
      const value = this.value.toLowerCase();
      closeAllLists();
      
      if (!value) return;
      
      const listDiv = document.createElement('div');
      listDiv.className = 'autocomplete-items';
      this.parentNode.appendChild(listDiv);
      
      cities.forEach(city => {
          if (city.toLowerCase().includes(value)) {
              const itemDiv = document.createElement('div');
              itemDiv.className = 'autocomplete-item';
              itemDiv.innerHTML = city.replace(new RegExp(value, 'gi'), `<strong>${value}</strong>`);
              
              itemDiv.addEventListener('click', function() {
                  input.value = city;
                  closeAllLists();
              });
              
              listDiv.appendChild(itemDiv);
          }
      });
  });
  
  input.addEventListener('keydown', function(e) {
      const items = document.querySelectorAll('.autocomplete-item');
      
      if (e.keyCode === 40) { // Down arrow
          currentFocus++;
          addActive(items);
      } else if (e.keyCode === 38) { // Up arrow
          currentFocus--;
          addActive(items);
      } else if (e.keyCode === 13) { // Enter
          e.preventDefault();
          if (currentFocus > -1 && items[currentFocus]) {
              items[currentFocus].click();
          }
      }
  });
  
  function addActive(items) {
      if (!items) return;
      removeActive(items);
      if (currentFocus >= items.length) currentFocus = 0;
      if (currentFocus < 0) currentFocus = items.length - 1;
      items[currentFocus].classList.add('autocomplete-active');
  }
  
  function removeActive(items) {
      items.forEach(item => item.classList.remove('autocomplete-active'));
  }
  
  function closeAllLists() {
      const items = document.querySelectorAll('.autocomplete-items');
      items.forEach(item => item.remove());
      currentFocus = -1;
  }
  
  // Close when clicking outside
  document.addEventListener('click', function(e) {
      if (!input.contains(e.target)) {
          closeAllLists();
      }
  });
}

// Booking System
function initBookingSystem() {
  const bookingForm = document.querySelector('.booking-form');
  const proceedButton = document.querySelector('.proceed-booking');
  
  if (proceedButton) {
      proceedButton.addEventListener('click', function() {
          if (selectedSeats.length === 0) {
              showNotification('Please select at least one seat', 'warning');
              return;
          }
          
          if (validateBookingForm()) {
              showBookingConfirmation();
          }
      });
  }
}

function validateBookingForm() {
  const requiredFields = document.querySelectorAll('.booking-form [required]');
  let isValid = true;
  
  requiredFields.forEach(field => {
      if (!field.value.trim()) {
          showFieldError(field, 'This field is required');
          isValid = false;
      }
  });
  
  // Validate phone number
  const phoneField = document.querySelector('#phone');
  if (phoneField && phoneField.value) {
      const phoneRegex = /^[0-9]{10}$/;
      if (!phoneRegex.test(phoneField.value)) {
          showFieldError(phoneField, 'Please enter a valid 10-digit phone number');
          isValid = false;
      }
  }
  
  // Validate email
  const emailField = document.querySelector('#email');
  if (emailField && emailField.value) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(emailField.value)) {
          showFieldError(emailField, 'Please enter a valid email address');
          isValid = false;
      }
  }
  
  return isValid;
}

function showBookingConfirmation() {
  const modal = document.createElement('div');
  modal.className = 'booking-modal';
  modal.innerHTML = `
      <div class="modal-content">
          <div class="modal-header">
              <h3>Confirm Your Booking</h3>
              <button class="close-modal">&times;</button>
          </div>
          <div class="modal-body">
              <div class="booking-details">
                  <h4>Journey Details</h4>
                  <p><strong>From:</strong> ${document.querySelector('#from-city').value}</p>
                  <p><strong>To:</strong> ${document.querySelector('#to-city').value}</p>
                  <p><strong>Date:</strong> ${document.querySelector('#journey-date').value}</p>
                  <p><strong>Bus:</strong> ${document.querySelector('.bus-name').textContent}</p>
                  <p><strong>Departure:</strong> ${document.querySelector('.departure-time').textContent}</p>
                  <p><strong>Selected Seats:</strong> ${selectedSeats.join(', ')}</p>
              </div>
              <div class="passenger-details">
                  <h4>Passenger Details</h4>
                  <p><strong>Name:</strong> ${document.querySelector('#passenger-name').value}</p>
                  <p><strong>Phone:</strong> ${document.querySelector('#phone').value}</p>
                  <p><strong>Email:</strong> ${document.querySelector('#email').value}</p>
              </div>
              <div class="payment-summary">
                  <h4>Payment Summary</h4>
                  <p><strong>Total Amount:</strong> Rs. ${(totalAmount + totalAmount * 0.05).toFixed(2)}</p>
              </div>
          </div>
          <div class="modal-footer">
              <button class="btn btn-secondary close-modal">Cancel</button>
              <button class="btn btn-primary confirm-booking">Confirm Booking</button>
          </div>
      </div>
  `;
  
  document.body.appendChild(modal);
  
  // Add event listeners
  const closeButtons = modal.querySelectorAll('.close-modal');
  closeButtons.forEach(btn => {
      btn.addEventListener('click', () => {
          document.body.removeChild(modal);
      });
  });
  
  const confirmButton = modal.querySelector('.confirm-booking');
  confirmButton.addEventListener('click', () => {
      processBooking();
      document.body.removeChild(modal);
  });
  
  // Close on outside click
  modal.addEventListener('click', (e) => {
      if (e.target === modal) {
          document.body.removeChild(modal);
      }
  });
}

function processBooking() {
  showLoadingState();
  
  const bookingData = {
      from_city: document.querySelector('#from-city').value,
      to_city: document.querySelector('#to-city').value,
      journey_date: document.querySelector('#journey-date').value,
      passenger_name: document.querySelector('#passenger-name').value,
      phone: document.querySelector('#phone').value,
      email: document.querySelector('#email').value,
      selected_seats: selectedSeats,
      total_amount: totalAmount + totalAmount * 0.05,
      bus_id: document.querySelector('.bus-card').dataset.busId
  };
  
  // Simulate API call
  setTimeout(() => {
      hideLoadingState();
      showNotification('Booking confirmed successfully! You will receive SMS and email confirmation.', 'success');
      
      // Reset form and seats
      selectedSeats = [];
      totalAmount = 0;
      updateBookingSummary();
      updateSeatCounter();
      
      // Clear selected seats
      document.querySelectorAll('.seat.selected').forEach(seat => {
          seat.classList.remove('selected');
      });
      
      // Redirect to booking confirmation page
      setTimeout(() => {
          window.location.href = '/booking-confirmation/';
      }, 2000);
  }, 2000);
}

// Notification System
function initNotifications() {
  // Create notification container if it doesn't exist
  if (!document.querySelector('.notification-container')) {
      const container = document.createElement('div');
      container.className = 'notification-container';
      document.body.appendChild(container);
  }
}

function showNotification(message, type = 'info', duration = 5000) {
  const container = document.querySelector('.notification-container');
  const notification = document.createElement('div');
  notification.className = `notification notification-${type}`;
  
  notification.innerHTML = `
      <div class="notification-content">
          <span class="notification-icon">${getNotificationIcon(type)}</span>
          <span class="notification-message">${message}</span>
          <button class="notification-close">&times;</button>
      </div>
  `;
  
  container.appendChild(notification);
  
  // Add event listener for close button
  const closeButton = notification.querySelector('.notification-close');
  closeButton.addEventListener('click', () => {
      removeNotification(notification);
  });
  
  // Auto remove after duration
  setTimeout(() => {
      removeNotification(notification);
  }, duration);
  
  // Add entrance animation
  setTimeout(() => {
      notification.classList.add('show');
  }, 10);
}

function removeNotification(notification) {
  notification.classList.add('hide');
  setTimeout(() => {
      if (notification.parentNode) {
          notification.parentNode.removeChild(notification);
      }
  }, 300);
}

function getNotificationIcon(type) {
  const icons = {
      'success': '✓',
      'error': '✗',
      'warning': '⚠',
      'info': 'ℹ'
  };
  return icons[type] || icons.info;
}

// Date Picker
function initDatePicker() {
  const dateInputs = document.querySelectorAll('input[type="date"]');
  
  dateInputs.forEach(input => {
      // Set minimum date to today
      const today = new Date().toISOString().split('T')[0];
      input.min = today;
      
      // Set maximum date to 30 days from today
      const maxDate = new Date();
      maxDate.setDate(maxDate.getDate() + 30);
      input.max = maxDate.toISOString().split('T')[0];
      
      // Add change event listener
      input.addEventListener('change', function() {
          const selectedDate = new Date(this.value);
          const currentDate = new Date();
          
          if (selectedDate < currentDate) {
              showNotification('Please select a future date', 'warning');
              this.value = today;
          }
      });
  });
}

// Mobile Menu
function initMobileMenu() {
  const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
  const mobileMenu = document.querySelector('.mobile-menu');
  
  if (mobileMenuToggle && mobileMenu) {
      mobileMenuToggle.addEventListener('click', function() {
          mobileMenu.classList.toggle('active');
          this.classList.toggle('active');
      });
      
      // Close menu when clicking outside
      document.addEventListener('click', function(e) {
          if (!mobileMenu.contains(e.target) && !mobileMenuToggle.contains(e.target)) {
              mobileMenu.classList.remove('active');
              mobileMenuToggle.classList.remove('active');
          }
      });
  }
}

// Tooltips
function initTooltips() {
  const tooltipElements = document.querySelectorAll('[data-tooltip]');
  
  tooltipElements.forEach(element => {
      element.addEventListener('mouseenter', function() {
          showTooltip(this);
      });
      
      element.addEventListener('mouseleave', function() {
          hideTooltip();
      });
  });
}

function showTooltip(element) {
  const tooltip = document.createElement('div');
  tooltip.className = 'tooltip';
  tooltip.textContent = element.dataset.tooltip;
  
  document.body.appendChild(tooltip);
  
  const rect = element.getBoundingClientRect();
  tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
  tooltip.style.top = rect.top - tooltip.offsetHeight - 10 + 'px';
  
  tooltip.classList.add('show');
}

function hideTooltip() {
  const tooltip = document.querySelector('.tooltip');
  if (tooltip) {
      tooltip.remove();
  }
}

// Payment Methods
function initPaymentMethods() {
  const paymentMethods = document.querySelectorAll('.payment-method');
  
  paymentMethods.forEach(method => {
      method.addEventListener('click', function() {
          // Remove active class from all methods
          paymentMethods.forEach(m => m.classList.remove('active'));
          
          // Add active class to clicked method
          this.classList.add('active');
          
          // Update hidden input if exists
          const hiddenInput = document.querySelector('#payment-method');
          if (hiddenInput) {
              hiddenInput.value = this.dataset.method;
          }
      });
  });
}

// Bus Filters
function initBusFilters() {
  const filterButtons = document.querySelectorAll('.filter-btn');
  const sortSelect = document.querySelector('#sort-buses');
  
  filterButtons.forEach(button => {
      button.addEventListener('click', function() {
          const filterType = this.dataset.filter;
          
          // Toggle active state
          this.classList.toggle('active');
          
          // Apply filters
          applyBusFilters();
      });
  });
  
  if (sortSelect) {
      sortSelect.addEventListener('change', function() {
          sortBuses(this.value);
      });
  }
}

function applyBusFilters() {
  const activeFilters = document.querySelectorAll('.filter-btn.active');
  const busCards = document.querySelectorAll('.bus-card');
  
  busCards.forEach(card => {
      let shouldShow = true;
      
      activeFilters.forEach(filter => {
          const filterType = filter.dataset.filter;
          const cardData = card.dataset;
          
          switch (filterType) {
              case 'ac':
                  if (cardData.ac !== 'true') shouldShow = false;
                  break;
              case 'sleeper':
                  if (cardData.type !== 'sleeper') shouldShow = false;
                  break;
              case 'wifi':
                  if (cardData.wifi !== 'true') shouldShow = false;
                  break;
              case 'charging':
                  if (cardData.charging !== 'true') shouldShow = false;
                  break;
          }
      });
      
      card.style.display = shouldShow ? 'block' : 'none';
  });
}

function sortBuses(sortBy) {
  const busContainer = document.querySelector('.bus-list');
  const busCards = Array.from(document.querySelectorAll('.bus-card'));
  
  busCards.sort((a, b) => {
      switch (sortBy) {
          case 'price-low':
              return parseFloat(a.dataset.price) - parseFloat(b.dataset.price);
          case 'price-high':
              return parseFloat(b.dataset.price) - parseFloat(a.dataset.price);
          case 'departure':
              return a.dataset.departure.localeCompare(b.dataset.departure);
          case 'duration':
              return parseFloat(a.dataset.duration) - parseFloat(b.dataset.duration);
          default:
              return 0;
      }
  });
  
  // Re-append sorted cards
  busCards.forEach(card => busContainer.appendChild(card));
}

// Loading States
function initLoadingStates() {
  // Add loading state to forms
  const forms = document.querySelectorAll('form');
  
  forms.forEach(form => {
      form.addEventListener('submit', function() {
          showLoadingState();
      });
  });
}

function showLoadingState() {
  const loader = document.createElement('div');
  loader.className = 'loading-overlay';
  loader.innerHTML = `
      <div class="loading-spinner">
          <div class="spinner"></div>
          <p>Processing your request...</p>
      </div>
  `;
  
  document.body.appendChild(loader);
}

function hideLoadingState() {
  const loader = document.querySelector('.loading-overlay');
  if (loader) {
      loader.remove();
  }
}

// AJAX Helper Functions
function makeAjaxRequest(url, method = 'GET', data = null) {
  return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      
      xhr.open(method, url, true);
      xhr.setRequestHeader('Content-Type', 'application/json');
      xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
      
      // Add CSRF token if available
      const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
      if (csrfToken) {
          xhr.setRequestHeader('X-CSRFToken', csrfToken.value);
      }
      
      xhr.onload = function() {
          if (xhr.status >= 200 && xhr.status < 300) {
              try {
                  const response = JSON.parse(xhr.responseText);
                  resolve(response);
              } catch (e) {
                  resolve(xhr.responseText);
              }
          } else {
              reject(new Error(`HTTP ${xhr.status}: ${xhr.statusText}`));
          }
      };
      
      xhr.onerror = function() {
          reject(new Error('Network error'));
      };
      
      xhr.send(data ? JSON.stringify(data) : null);
  });
}

// Utility Functions
function formatCurrency(amount) {
  return `Rs. ${amount.toFixed(2)}`;
}

function formatTime(time) {
  const [hours, minutes] = time.split(':');
  const hour = parseInt(hours);
  const ampm = hour >= 12 ? 'PM' : 'AM';
  const displayHour = hour % 12 || 12;
  
  return `${displayHour}:${minutes} ${ampm}`;
}

function formatDate(date) {
  const options = { year: 'numeric', month: 'long', day: 'numeric' };
  return new Date(date).toLocaleDateString('en-US', options);
}

function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
      const later = () => {
          clearTimeout(timeout);
          func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
  };
}

// Error Handling
window.addEventListener('error', function(e) {
  console.error('JavaScript Error:', e.error);
  showNotification('An error occurred. Please try again.', 'error');
});

window.addEventListener('unhandledrejection', function(e) {
  console.error('Unhandled Promise Rejection:', e.reason);
  showNotification('A network error occurred. Please check your connection.', 'error');
});

// Initialize page-specific functionality
function initPageSpecific() {
  const page = document.body.dataset.page;
  
  switch (page) {
      case 'home':
          initHomePage();
          break;
      case 'bus-list':
          initBusListPage();
          break;
      case 'booking':
          initBookingPage();
          break;
      case 'profile':
          initProfilePage();
          break;
  }
}

function initHomePage() {
  // Initialize popular routes
  const popularRoutes = document.querySelectorAll('.popular-route');
  popularRoutes.forEach(route => {
      route.addEventListener('click', function() {
          const from = this.dataset.from;
          const to = this.dataset.to;
          
          document.querySelector('#from-city').value = from;
          document.querySelector('#to-city').value = to;
      });
  });
}

function initBusListPage() {
  // Initialize bus list specific functionality
  const busCards = document.querySelectorAll('.bus-card');
  
  busCards.forEach(card => {
      const selectButton = card.querySelector('.select-bus');
      if (selectButton) {
          selectButton.addEventListener('click', function() {
              const busId = card.dataset.busId;
              window.location.href = `/booking/${busId}/`;
          });
      }
  });
}

function initBookingPage() {
  // Initialize booking page specific functionality
  const passengerInputs = document.querySelectorAll('.passenger-input');
  
  passengerInputs.forEach(input => {
      input.addEventListener('input', debounce(function() {
          validateBookingForm();
      }, 300));
  });
}

function initProfilePage() {
  // Initialize profile page specific functionality
  const bookingCards = document.querySelectorAll('.booking-card');
  
  bookingCards.forEach(card => {
      const cancelButton = card.querySelector('.cancel-booking');
      if (cancelButton) {
          cancelButton.addEventListener('click', function() {
              const bookingId = card.dataset.bookingId;
              confirmCancelBooking(bookingId);
          });
      }
  });
}

function confirmCancelBooking(bookingId) {
  if (confirm('Are you sure you want to cancel this booking?')) {
      // Make API call to cancel booking
      makeAjaxRequest(`/api/cancel-booking/${bookingId}/`, 'POST')
          .then(response => {
              if (response.success) {
                  showNotification('Booking cancelled successfully', 'success');
                  location.reload();
              } else {
                  showNotification('Failed to cancel booking', 'error');
              }
          })
          .catch(error => {
              showNotification('Error cancelling booking', 'error');
          });
  }
}

// Initialize everything when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
  initPageSpecific();
});