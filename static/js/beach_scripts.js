
// Section 1: Reply Button Toggle
document.addEventListener('DOMContentLoaded', function() {
  const replyButtons = document.querySelectorAll('.btn-reply');

  replyButtons.forEach(button => {
    button.addEventListener('click', function() {
      const messageId = this.getAttribute('data-message-id');
      const replyForm = document.querySelector('#reply-form');

      // Set the message ID to the hidden input field
      replyForm.querySelector('input[name="reply_to_message_id"]').value = messageId;

      // Toggle visibility of the reply form
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

// Section 2: Toggle Replies
function toggleReplies(messageId) {
  var replies = document.getElementById('replies-' + messageId);
  var button = event.target;

  // Toggle visibility of replies
  if (replies.style.display === "none") {
    replies.style.display = "block";
    button.textContent = "Hide Replies";
  } else {
    replies.style.display = "none";
    button.textContent = "View Replies";
  }
}

// Section 3: Emoji Picker for Replies
document.addEventListener('DOMContentLoaded', function() {
  const replyEmojiPickerBtns = document.querySelectorAll('#emoji-picker-bt'); // Select all emoji picker buttons for replies
  const replyEmojiPickers = document.querySelectorAll('#emoji-picke'); // Select all emoji pickers
  const replyTextAreas = document.querySelectorAll('#content1'); // Select all reply text areas

  // List of emojis
  const emojis = ['😀', '😂', '😍', '🤔', '😢', '😎'];

  // Loop through each reply section
  replyEmojiPickerBtns.forEach((btn, index) => {
    const emojiPicker = replyEmojiPickers[index]; // Corresponding emoji picker
    const textArea = replyTextAreas[index]; // Corresponding text area

    // Add emojis to the picker
    emojis.forEach(emoji => {
      const emojiElem = document.createElement('span');
      emojiElem.classList.add('emoji-item');
      emojiElem.textContent = emoji;
      emojiElem.addEventListener('click', () => {
        textArea.value += emoji; // Append emoji to the corresponding text area
        emojiPicker.style.display = 'none'; // Hide picker after selection
      });
      emojiPicker.appendChild(emojiElem);
    });

    // Toggle emoji picker visibility for each button
    btn.addEventListener('click', (event) => {
      emojiPicker.style.display = emojiPicker.style.display === 'block' ? 'none' : 'block';
    });

    // Hide emoji picker when clicking outside
    document.addEventListener('click', (event) => {
      if (!btn.contains(event.target) && !emojiPicker.contains(event.target)) {
        emojiPicker.style.display = 'none';
      }
    });
  });
});

// Section 4: Emoji Picker for Main Text Area
document.addEventListener('DOMContentLoaded', function() {
  const emojiPickerBtn = document.getElementById('emoji-picker-btn');
  const emojiPicker = document.getElementById('emoji-picker');
  const textArea = document.getElementById('content');

  // Emoji list
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

// Section 5: Pagination
document.addEventListener('DOMContentLoaded', function() {
  const rowsPerPage = 7;
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

// Section 6: Scroll to Bottom of Chat Messages
document.addEventListener('DOMContentLoaded', function() {
  function scrollToBottom() {
    const chatMessages = document.querySelector('.chat-messages');
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  // Scroll to bottom on page load
  scrollToBottom();
});

// Section 7: Format Date and Time
document.addEventListener('DOMContentLoaded', function() {
  function formatDateTime(dateTimeString) {
    const date = new Date(dateTimeString);
    const options = { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' };
    return date.toLocaleString('en-US', options).replace(',', ''); // Remove the comma between date and time
  }

  // Apply formatting to all timestamps
  document.querySelectorAll('.time').forEach(function(element) {
    element.textContent = formatDateTime(element.textContent);
  });
});

// Section 8: Toggle Replies and Reply Form
function toggleReplies(replyId) {
  var repliesDiv = document.getElementById(replyId);
  if (repliesDiv.style.display === "none" || repliesDiv.style.display === "") {
    repliesDiv.style.display = "block"; // Show the replies
  } else {
    repliesDiv.style.display = "none"; // Hide the replies
  }
}

function toggleReplyForm(commentId) {
  var replyForm = document.getElementById('reply-form-' + commentId);
  if (replyForm.style.display === "none" || replyForm.style.display === "") {
    replyForm.style.display = "block"; // Show the reply form
  } else {
    replyForm.style.display = "none"; // Hide the reply form
  }
}

// Section 9: Initialize Leaflet Map with Markers
var map = L.map("map").setView([-33.9249, 18.4241], 11); // Centered on Cape Town

// Add a tile layer (the background map)
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 18,
}).addTo(map);

// Add markers for each beach (example marker)
L.marker([-33.941, 18.377])
  .addTo(map);

