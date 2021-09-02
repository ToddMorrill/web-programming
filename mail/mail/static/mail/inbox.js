document.addEventListener('DOMContentLoaded', function () {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // is this where we want to install the form.onsubmit listener?
  document.querySelector('form').onsubmit = function () {
    const recipients = document.querySelector('#compose-recipients').value
    const subject = document.querySelector('#compose-subject').value
    const body = document.querySelector('#compose-body').value
    fetch('/emails', {
      method: 'POST',
      body: JSON.stringify({
        recipients: recipients,
        subject: subject,
        body: body
      })
    })
      .then(response => response.json())
      .then(result => { console.log(result); })

    // redirect user to their sent box
    load_mailbox('sent');

    // don't submit the form (and force a redirect)
    return false
  };

  // By default, load the inbox
  load_mailbox('inbox');
});

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';
  document.querySelector('#email-view').style.display = 'none';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';

}

function view_email(mailbox, email) {
  // placeholder for html elements
  var elements = [];

  // Mark the email as read
  fetch(`/emails/${email.id}`, {
    method: 'PUT',
    body: JSON.stringify({
      read: true
    })
  })
  
  // clear any existing content
  document.querySelector('#email-view').innerHTML = '';

  // Show email view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'block';

  const from = document.createElement('div');
  from.innerHTML = `<b>From:</b> ${email.sender}`;
  elements.push(from)
  const to = document.createElement('div');
  to.innerHTML = `<b>To:</b> ${email.recipients}`;
  elements.push(to)
  const subject = document.createElement('div');
  subject.innerHTML = `<b>Subject:</b> ${email.subject}`;
  elements.push(to)
  const timestamp = document.createElement('div');
  timestamp.innerHTML = `<b>Timestamp:</b> ${email.timestamp}`;
  elements.push(timestamp)

  // add in reply button and (un)archive button
  // const button_div = document.createElement('div');
  // button_div.setAttribute('id', 'button-div');
  const reply = document.createElement('button');
  reply.textContent = 'Reply';
  reply.setAttribute('class', 'btn btn-sm btn-outline-primary');
  elements.push(reply)
  // add event listener to the button
  reply.onclick = function() {}
  if (mailbox != 'sent') {
    // add archive button if inbox or archive
    const archive = document.createElement('button');
    archive.setAttribute('class', 'btn btn-sm btn-outline-primary');
    if (email.archived) {
      archive.textContent = 'Unarchive';
      archive.onclick = function() {
        fetch(`/emails/${email.id}`, {
          method: 'PUT',
          body: JSON.stringify({
            archived: false
          })
        });
        // send user to their inbox and return
        return load_mailbox('inbox')
      }
    }
    else {
      archive.textContent = 'Archive';
      archive.onclick = function() {
        fetch(`/emails/${email.id}`, {
          method: 'PUT',
          body: JSON.stringify({
            archived: true
          })
        });
        return load_mailbox('inbox')
      }
    }
    elements.push(archive)
  }
  
  const line = document.createElement('hr')
  elements.push(line)

  const body = document.createElement('div');
  body.innerHTML = email.body
  elements.push(body)

  document.querySelector('#email-view').append(...elements)

}

function email_entry(mailbox, email) {
  // create div objects for each of the emails
  const div = document.createElement('div');
  div.setAttribute('class', 'border rounded email');

  // create inner divs
  const names = document.createElement('div');
  names.setAttribute('class', 'email-components names');
  const subject = document.createElement('div');
  subject.setAttribute('class', 'email-components subject');
  const timestamp = document.createElement('div');
  timestamp.setAttribute('class', 'email-components timestamp');

  if (mailbox === 'sent') {
    names.innerHTML = email.recipients;
    subject.innerHTML = email.subject;
    timestamp.innerHTML = email.timestamp;
    div.append(names);
    div.append(subject);
    div.append(timestamp);
  }
  else {
    // inbox and archive
    names.innerHTML = email.sender
    subject.innerHTML = email.subject
    timestamp.innerHTML = email.timestamp
    div.append(names);
    div.append(subject);
    div.append(timestamp);

    // add formatting based on read status
    if (email.read) {
      div.setAttribute('class', 'border rounded email read');
    }
    else {
      div.setAttribute('class', 'border rounded email unread');
    }

  }

  // install click event handler for the div
  div.onclick = function () {
    fetch(`/emails/${email.id}`)
      .then(response => response.json())
      .then(view_email.bind(null, mailbox))
  }

  document.querySelector('#emails-view').append(div)

}

function load_mailbox(mailbox) {

  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  // create placeholder unordered list
  // const ul = document.createElement('ul', id='emails-list')
  // ul.setAttribute('id', 'emails-list');
  // document.querySelector('#emails-view').append(ul)

  // Load the appropriate mailbox
  fetch(`/emails/${mailbox}`)
    .then(response => response.json())
    .then(response => {
      response.forEach(email_entry.bind(null, mailbox))
    })
}