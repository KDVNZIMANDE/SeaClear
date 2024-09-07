document.addEventListener('DOMContentLoaded', function() {
    var pinIcon = document.getElementById('pinIcon');
  
    pinIcon.addEventListener('click', function(event) {
      event.preventDefault(); // Prevent the default action (if any)
      pinIcon.classList.toggle('active'); // Toggle the 'active' class
    });
  });
  