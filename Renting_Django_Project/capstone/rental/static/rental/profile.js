document.addEventListener('DOMContentLoaded', function() {
    if (initial_section) { // initial_section initialized in script block in profile.html
        if (initial_section.includes('dialog-')) {
            load_dialog(parseInt(initial_section.slice(7)));
            show_block("#profile-dialog", "#btn-dialogs");
        } else {
            show_block(`#profile-${initial_section}`, `#btn-${initial_section}`);
        }
    } else {
        show_block("#profile-userdata", "#btn-userdata");
    }

    // Initially load all user's data(userdata, ads, dialogs).
    refresh();

    document.querySelector('#btn-userdata').addEventListener('click', () => show_block('#profile-userdata', '#btn-userdata'));
    document.querySelector('#btn-ads').addEventListener('click', () => show_block('#profile-ads', '#btn-ads'));
    document.querySelector('#btn-saved').addEventListener('click', () => show_block('#profile-saved', '#btn-saved'));
    document.querySelector('#btn-dialogs').addEventListener('click', () => show_block('#profile-dialogs', '#btn-dialogs'));
    document.querySelector('#btn-refresh').addEventListener('click', refresh);

    window.onpopstate = function(event) {
        if (event.state && event.state.section.includes("profile-dialog-")) {
            load_dialog(event.state.section.slice("profile-dialog-".length));
            show_block("#profile-dialog", "#btn-dialogs");
        } else if (event.state) {
            show_block(`#${event.state.section}`, `#btn-${event.state.section.slice(8)}`);
        } else if (initial_section) {
            if (initial_section.includes('dialog-')) {
                load_dialog(parseInt(initial_section.slice(7)));
                show_block("#profile-dialog", "#btn-dialogs");
            } else {
                show_block(`#profile-${initial_section}`, `#btn-${initial_section}`);
            }
        } else {
            show_block('#profile-userdata', '#btn-userdata');
        }
    }

    document.querySelectorAll(".profile-section").forEach(button => {
        button.onclick = function() {
            const section = this.dataset.section;
            history.pushState({section: section}, "", `${section}`);
        };
    });

    document.querySelector("#send-message").onclick = function(event) {
        event.preventDefault();
        textarea = document.querySelector("#id_text");
        text = textarea.value;
        textarea.value = ""; // Frees textarea.
        dialog = document.querySelector("#messages .dialog-info");
        let dialog_id = dialog.id.slice(3);
        new_message(dialog_id, text);
    };
});

function show_block(block, button) {
    if (button === "#btn-dialog") {
        button = "#btn-dialogs";
    }
    // Show 'block' and hide all others.
    const blocks = ['#profile-userdata', '#profile-ads', '#profile-saved', '#profile-dialogs', '#profile-dialog'];
    for (let block of blocks) {
        document.querySelector(block).style.display = 'none';
    }
    document.querySelectorAll("#profile-navbar button").forEach(button => {
        button.style["background-color"] = 'ghostwhite';
    });
    document.querySelector(button).style["background-color"] = 'lavender';
    document.querySelector(block).style.display = 'block';
}

function show_ads(data, type) {
    // Return all ads as a string to use in load_ads and load_saved functions.
    let button;
    // For ads in users ads section.
    if (type === "user_ads") {
        button = `<button class="btn btn-secondary btn-sm activate-btn"></button>
                  <button class="btn btn-secondary btn-sm edit-btn">Edit</button>`;
    }
    // For ads in saved ads section.
    else if (type === "saved") {
        button = '<button class="btn btn-secondary btn-sm btn-remove">Remove</button>';
    }
    let content = { "active": "",
                    "not-active": "" };
    for (let ad of data) {
        let adContent = `<div class="ads-header row">
                            <div class="ads-title">${ad.title} | <b>${ad.city}</b></div>
                         </div>
                         <div class="ads-description">${ad.description}</div>
                         <div class="ads-price">Price $: ${ad.price}</div>
                         <div class="ads-creation">Creation date: ${ad.creation_date}</div>`;
        if (ad.isactive) {
            content["active"] += `<div id="ad-${ad.id}" class="ad-post">${adContent}${button}</div>`;
        } else {
            content["not-active"] += `<div id="ad-${ad.id}" class="ad-post not-active">${adContent}${button}</div>`;
        }
    }
    return content;
}


function load_ads() {
    fetch('profile/load_ads')
    .then(response => response.json())
    .then(data => {
        if (!data) {
            document.querySelector('#profile-ads .active').innerHTML = '<div class="ad-post">You have no ads yet.</div>';
        } else {
            let ads = show_ads(data, "user_ads");
            document.querySelector('#profile-ads .active').innerHTML = ads["active"];
            document.querySelector('#profile-ads .not-active').innerHTML = ads["not-active"];

            // Hide price field from not active ads.
            ads_price = document.querySelectorAll('#profile-ads .not-active .ads-price');
            ads_price.forEach(price => {
                price.style.display = "none";
            });

            document.querySelectorAll('#profile-ads .ad-post').forEach(ad => {
                let ad_id = ad.id.slice(3);
                // Button to active and deactivate users ads.
                document.querySelector(`#ad-${ad_id} .activate-btn`).onclick = function() {
                    change_active(ad_id);
                };
                // Link to ad page.
                ad.querySelector(`#ad-${ad_id} .ads-title`).onclick = function() {
                    window.location.href = `ad-${ad.id.slice(3)}`;
                }; // Edit page link.
                ad.querySelector(`#ad-${ad_id} .edit-btn`).onclick = function() {
                    window.location.href = `edit/${ad.id.slice(3)}`;
                };
            });
            //  Change button label.
            document.querySelectorAll(".active .ad-post .activate-btn").forEach(button => {
                button.innerHTML = "Archive";
            });
            document.querySelectorAll(".not-active .ad-post .activate-btn").forEach(button => {
                button.innerHTML = "Back to active";
            });
        }
    });
}

function load_saved() {
    fetch('profile/load_saved')
    .then(response => response.json())
    .then(data => {
        if (!data) {
            document.querySelector('#profile-saved .active').innerHTML = '<div class="ad-post">You have no saved ads.</div>';
        } else {
            let ads = show_ads(data, "saved");
            document.querySelector('#profile-saved .active').innerHTML = ads["active"];
            document.querySelector('#profile-saved .not-active').innerHTML = ads["not-active"];

            ads_price = document.querySelectorAll('#profile-saved .not-active .ads-price');
            ads_price.forEach(price => {
                price.style.display = "none";
            });

            // Create "remove" button
            document.querySelectorAll("#profile-saved .ad-post").forEach(ad => {
                let ad_id = ad.id.slice(3);
                let remove_button = document.querySelector(`#profile-saved #ad-${ad_id} .btn-remove`);
                if (remove_button) {
                    remove_button.onclick = () => {
                        remove(ad_id);
                    }
                }
                ad.querySelector(`#ad-${ad_id} .ads-title`).onclick = function() {
                    window.location.href = `ad-${ad.id.slice(3)}`;
                }
            });
        }
    })
}

function load_dialogs() {
    function show_dialogs(data) {
        let content = "";
        for (let dialog of data) {
            let new_msg = '';
            if (!dialog.is_read) {
                new_msg = '<div class="dialog-newmsg">New message!</div>';
            }
            content += `<div id="dialog-${dialog.id}" class="dialog">
                          <div class="dialog-header">
                            <div class="dialog-user"><i>${dialog.user}</i></div>
                            <div class="dialog-ad-title">${dialog.ad_title} | <b>${dialog.ad_city}</b></div>
                            <div class="dialog-ad-price">${dialog.ad_price}$</div>
                            ${new_msg}
                          </div>
                            <div class="dialog-lastmsg">Last message: ${dialog.last_message_text}</div>
                            <dive class="dialog-datetime">${dialog.last_message_date}</div>
                        </div>`
        }
        return content
    }
    fetch('profile/dialogs')
    .then(response => response.json())
    .then(data => {
        if (!data) {
            document.querySelector('#profile-dialogs').innerHTML = '<div class="dialog">You have no dialogs.</div>';
        } else {
            document.querySelector('#profile-dialogs').innerHTML = show_dialogs(data);
            document.querySelectorAll('.dialog').forEach(dialog => {
                dialog.querySelector('.dialog-header').onclick = function() {
                    let dialog_id = dialog.id.slice(7)
                    load_dialog(dialog_id);
                    history.pushState({section: `profile-dialog-${dialog_id}`}, "", `profile-dialog-${dialog_id}`);
                }
            });
        }
    });
}

function load_dialog(dialog_id) {
    function show_dialog(data) {
        let content = `<div id="id-${data.id}" class="dialog-info">${data.ad_title} | <b>${data.ad_city}</b> - $${data.ad_price}
                            <button id="dialog-update" class="btn btn-secondary">Update</button>
                        </div>`;
        for (let message of data.messages) {
            let message_class;
            if (logged_user === message.author) {
                message_class = "message user-message";
            } else {
                message_class = "message not-user-message";
            }
            content += `<div class="${message_class}">
                            <div class="message-author">${message.author}</div>
                            <div class="message-text">${message.text}</div>
                            <div class="message-creation-date">${message.datetime}</div>
                        </div>`;
        }
        return content
    }

    fetch(`profile/dialog/${dialog_id}`)
    .then(response => response.json())
    .then(data => {
        document.querySelector('#profile-dialog #messages').innerHTML = show_dialog(data);
        document.querySelector('#dialog-update').onclick = function() {
            messages_block = document.querySelector('#profile-dialog #messages')
            messages_block.style.display = "none";
            load_dialog(dialog_id);
            setTimeout(function() {
                messages_block.style.display = "flex";
            }, 500);
        }
        show_block('#profile-dialog', '#btn-dialogs');
        update_spans();
        load_dialogs(); // To update "read" status.
    });
}

function refresh() {
    // Update all changes on profile page.
    body_block = document.querySelector('.profile-body')
    body_block.style.display = "none";
    load_ads();
    load_saved();
    load_dialogs();
    update_spans();
    setTimeout(function() {
        body_block.style.display = "";
    }, 500);
}

function update_spans() {
    fetch(`profile/update`)
    .then(response => response.json())
    .then(data => {
        document.querySelector("#btn-saved span").innerHTML = data.saved_ads_num;
        let dialog_span = document.querySelector("#btn-dialogs span");
        if (data.unread_dialogs === 0) {
            dialog_span.style.display = 'none';
        } else {
            dialog_span.style.display = 'inline';
            dialog_span.innerHTML = data.unread_dialogs;
        }
    });
}

function remove(id) {
    // Remove ad from saved ads.
    const csrftoken = getCookie('csrftoken');
    fetch(`/ad/save/${id}`, {
        method: 'PUT',
        headers: {'X-CSRFToken': csrftoken}
    })
    .then(response => response.json())
    .then(data => {
        load_saved();
        update_spans();
    });
}

function change_active(id) {
    const csrftoken = getCookie('csrftoken');
    fetch(`/ad/activate/${id}`, {
        method: 'PUT',
        headers: {'X-CSRFToken': csrftoken}
    })
    .then(response => response.json())
    .then(data => {
        load_ads();
    });
}

function new_message(id, text) {
    const csrftoken = getCookie('csrftoken');
    fetch(`profile/message/${id}`, {
        method: 'POST',
        headers: {'X-CSRFToken': csrftoken},
        body: JSON.stringify({
            "text": text
            })
        })
        .then(response => response.json())
        .then(data => {
            // Reload section to show new message sent.
            load_dialog(id);
            load_dialogs();
        });
}
