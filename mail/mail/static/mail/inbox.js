document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // is this where we want to install the form.onsubmit listener?
  document.querySelector('form').onsubmit = function() {
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
    .then(result => {console.log(result);})
    
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

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
  
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

      
    document.querySelector('#emails-view').append(div)
}

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';

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