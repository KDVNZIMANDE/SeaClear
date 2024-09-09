document.addEventListener('DOMContentLoaded', function() {
    var pinIcon = document.getElementById('pinIcon');
  
    pinIcon.addEventListener('click', function(event) {
      event.preventDefault(); // Prevent the default action (if any)
      pinIcon.classList.toggle('active'); // Toggle the 'active' class
    });
  });
  
  document.addEventListener('DOMContentLoaded', function() {
    const replyButtons = document.querySelectorAll('.btn-reply');
    
    replyButtons.forEach(button => {
      button.addEventListener('click', function() {
        const messageId = this.getAttribute('data-message-id');
        const replyForm = document.querySelector('#reply-form');
        
        // Set the message ID to the hidden input field
        replyForm.querySelector('input[name="reply_to_message_id"]').value = messageId;
        
        // Display the reply form and focus on the textarea
        // Toggle visibility of reply form
        if (replyForm.style.display === 'block') {
          replyForm.style.display = 'none'; // Hide form if it's already visible
      } else {
          replyForm.style.display = 'block'; // Show form if it's hidden
          replyForm.querySelector('textarea[name="reply_content"]').focus();
      }
               
        // Scroll to the reply form
        replyForm.scrollIntoView({ behavior: 'smooth' });
      });
    });
  });

  function toggleReplies(messageId) {
    var replies = document.getElementById('replies-' + messageId);
    var button = event.target;

    if (replies.style.display === "none") {
        replies.style.display = "block";
        button.textContent = "Hide Replies";
    } else {
        replies.style.display = "none";
        button.textContent = "View Replies";
    }
}



document.addEventListener('DOMContentLoaded', function() {
  const emojiPickerBtn = document.getElementById('emoji-picker-btn');
  const emojiPicker = document.getElementById('emoji-picker');
  const textArea = document.getElementById('content');
  
  // Emoji list (you can use a library to generate this)
  const emojis = ['😀', '😂', '😍', '🤔', '😢', '😎'];
  emojis.forEach(emoji => {
      const emojiElem = document.createElement('span');
      emojiElem.classList.add('emoji-item');
      emojiElem.textContent = emoji;
      emojiElem.addEventListener('click', () => {
          textArea.value += emoji; // Append selected emoji to the text area
          emojiPicker.style.display = 'none'; // Hide picker after selection
      });
      emojiPicker.appendChild(emojiElem);
  });

  // Toggle emoji picker visibility
  emojiPickerBtn.addEventListener('click', () => {
      emojiPicker.style.display = emojiPicker.style.display === 'block' ? 'none' : 'block';
  });

  // Hide emoji picker when clicking outside
  document.addEventListener('click', (event) => {
      if (!emojiPickerBtn.contains(event.target) && !emojiPicker.contains(event.target)) {
          emojiPicker.style.display = 'none';
      }
  });
});

document.addEventListener('DOMContentLoaded', function() {
  const rowsPerPage = 10;
  const tableBody = document.getElementById('table-body');
  const rows = Array.from(tableBody.querySelectorAll('tr'));
  const totalPages = Math.ceil(rows.length / rowsPerPage);
  let currentPage = 1;

  const prevBtn = document.getElementById('prev-btn');
  const nextBtn = document.getElementById('next-btn');
  const pageInfo = document.getElementById('page-info');

  function showPage(page) {
    const startRow = (page - 1) * rowsPerPage;
    const endRow = page * rowsPerPage;

    rows.forEach((row, index) => {
      if (index >= startRow && index < endRow) {
        row.style.display = 'table-row';
      } else {
        row.style.display = 'none';
      }
    });

    pageInfo.textContent = `Page ${page} of ${totalPages}`;

    // Enable/Disable buttons
    prevBtn.disabled = page === 1;
    nextBtn.disabled = page === totalPages;
  }

  // Initial page load
  showPage(currentPage);

  // Event listeners for buttons
  prevBtn.addEventListener('click', function() {
    if (currentPage > 1) {
      currentPage--;
      showPage(currentPage);
    }
  });

  nextBtn.addEventListener('click', function() {
    if (currentPage < totalPages) {
      currentPage++;
      showPage(currentPage);
    }
  });
});

