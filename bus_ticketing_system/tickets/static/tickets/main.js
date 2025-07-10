

document.addEventListener('DOMContentLoaded', function () {
    const seatButtons = document.querySelectorAll('.seat.available');
    const seatInput = document.getElementById('seatInput');
    const selectedDisplay = document.getElementById('selectedSeat');
  
    seatButtons.forEach(button => {
      button.addEventListener('click', () => {
        seatButtons.forEach(btn => btn.classList.remove('selected'));
        button.classList.add('selected');
        const seatNumber = button.dataset.seat;
        seatInput.value = seatNumber;
        selectedDisplay.textContent = seatNumber;
      });
    });
  });
  