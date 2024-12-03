document.addEventListener('DOMContentLoaded', function() {
    // Function implemented in the layout.js file.
    getCities("united states").then(data => {
        const cities = data;

        datalist = document.querySelector("#cities");
        // Add each city as an option to the filter input "city"
        cities.forEach(city => {
            const option = document.createElement('option');
            option.value = city;
            datalist.appendChild(option);
        });
    });

    window.onpopstate = function(event) {
        if (event.state) {
            if (event.state.section === "main") {
                show_block('#ads-block');
            } else {
                load_ad(event.state.section);
            }
        } else {
            let fullUrl = window.location.href;
            if (fullUrl.includes("ad-")) {
                load_ad(ad_id_init);
            } else {
                show_block("#ads-block");
            }
        }
    }

    // Load block depending on url (ad-x or main)
    const fullUrl = window.location.href;
    if (fullUrl.includes("ad-")) {
        load_ad(ad_id_init);
    } else {
        show_block("#ads-block");
    }

    // Add animation hide/show filter block.
    let show_filter = document.querySelector('#show-filter');
    let filter = document.querySelector('#filter-block');
    filter.style.animationName = "show";
    if (show_filter) {
        filter.addEventListener('animationend', function() {
            filter.style.animationPlayState = 'paused';
            if (filter.style.animationName === 'show') {
                filter.style.animationName = 'hide';
            } else {
                filter.style.animationName = 'show';
                filter.style.display = "none";
            }
        });
        show_filter.onclick = function() {
            if (filter.style.animationName === 'show') {
                filter.style.display = "block";
			    filter.style.animationPlayState = 'running';
			}  else {
			    filter.style.animationPlayState = 'running';
            }
		}
    }

    // Add save button and link to ad.
    document.querySelectorAll(".ad-post").forEach(ad => {
        let ad_id = ad.id.slice(3);
        let save_button = document.querySelector(`#ad-${ad_id} .ads-save`);
        if (save_button) {
            is_saved(ad_id);
            save_button.onclick = () => {
                to_saved(ad_id);
            }
        }
        document.querySelector(`#ad-${ad_id} .ads-title`).onclick = () => {
            history.pushState({section: ad_id}, "", `ad-${ad_id}`);
            load_ad(ad_id);
        }
    });

    // Add sorting functionality
    document.querySelectorAll(".ordering").forEach(element => {
        element.onclick = function() {
            order = element.value;
            ordering(order);
        };
    });
});

function show_block(block) {
    const blocks = ['#ads-block', '#ad-block'];
    for (let block of blocks) {
        document.querySelector(block).style.display = 'none';
    }
    document.querySelector(block).style.display = 'block';
}

function show_ad(data, ad_id) {
    // Fill ad-block with data when load_ad() is called.
    if (!data.isactive) {
        document.querySelector('#ad-block').classList.add("non-active-ad");
    } else {
        document.querySelector('#ad-block').classList.remove("non-active-ad");
    }
    let isavailable;
    if (data.isavailable) {
        isavailable = "now";
    } else {
        isavailable = data.available_from;
    }
    let image_url;
    if (data.image_url) {
        image_url = `<img src="${data.image_url}" alt="Ad Image" class="img-thumbnail align-self-start mr-3" style="max-width: 400px; max-height: 225px; width: auto; height: auto;" >`
    } else {
        image_url = ""
    }
    let furniture;
    if (data.furniture) {
        furniture = "Yes";
    } else {
        furniture = "No";
    }
    let content = `<div id="ad-${ad_id}" class="ad-title">${data.title} | <b>${data.city}</b></div>
                        <button id="edit-btn" class="btn btn-secondary" style="display: none;">Edit</button>
                       ${image_url}
                       <div class="ad-price"><b>Price $: ${data.price}</b></div>
                       <div class="ad-description">Description: ${data.description}</div>
                       <div class="ad-attributes">
                            <div class="ad-attr ad-rooms">Rooms: ${data.rooms}</div>
                            <div class="ad-attr ad-furniture">Furniture: ${furniture}</div>
                            <div class="ad-attr ad-availability">Available from: ${isavailable}</div>
                       </div>
                       `;
    document.querySelector('#ad-block #ad-content').innerHTML = `${content}`;
    ad_block_author = document.querySelector('#ad-block #author');
    if (ad_block_author) {
        ad_block_author.innerHTML = `${data.author} <div>Tel. ${data.phone}</div>`;
    }
}

function load_ad(ad_id) {
    fetch(`ad/${ad_id}`)
    .then(response => response.json())
    .then(data => {
        show_ad(data, ad_id);
        // Hide contact block if ad is archived or it is user's ad.
        if (!data.isactive) {
            document.querySelector("#ad-contact").style.display = "none";
        } else if (data.is_author) {
            document.querySelector("#ad-contact").style.display = "none";
            document.querySelector("#edit-btn").style.display = "block";
            document.querySelector("#edit-btn").onclick = function() {
                window.location.href = `edit/${ad_id}`;
            };
        } else {
            ad_block_contact = document.querySelector('#ad-contact');
            if (ad_block_contact) {
                document.querySelector("#ad-contact").style.display = "block";
                // Show and hide contact block on click.
                document.querySelector("#show-message").onclick = function(event) {
                    contact_form = document.querySelector(".contact-form");
                    if (contact_form.style.display === "none") {
                        contact_form.style.display = "block";
                    } else {
                        contact_form.style.display = "none";
                    }
                }
            }
        }

        send_message_btn = document.querySelector("#message-window #message-send");
        if (send_message_btn) {
            document.querySelector("#message-window #message-send").onclick = function(event) {
                event.preventDefault();
                textarea = document.querySelector("#message-window #message-text");
                text = textarea.value;
                ad_id = document.querySelector(".ad-title").id.slice(3);
                new_message(ad_id, text);
                textarea.value = '';
            }
        }

        show_block("#ad-block"); // Show the whole block only when all data is loaded.
    });
}

function is_saved(id) {
    // Change save button label if ad is in user's saved or not. "Save" by default
    fetch(`/ad/is_saved/${id}`)
    .then(response => response.json())
    .then(data => {
        let save_button = document.querySelector(`#ad-${id} .ads-save`);
        if (save_button && data.message === 'saved') {
            save_button.style = "display: block;";
            save_button.innerHTML = "Saved";
        }
        else if (save_button) {
            save_button.style = "display: block;";
        }
    });
}

function to_saved(id) {
    // Add or remove ad from saved ads.
    const csrftoken = getCookie('csrftoken');
    fetch(`/ad/save/${id}`, {
        method: 'PUT',
        headers: {'X-CSRFToken': csrftoken}
    })
    .then(response => response.json())
    .then(data => {
        let save_button = document.querySelector(`#ad-${id} .ads-save`);
        if (data.message === 'saved') {
            save_button.innerHTML = "Saved";
        }
        else if (save_button) {
            save_button.innerHTML = "Save";
        }
    });
}

function new_message(ad_id, text) {
    const csrftoken = getCookie('csrftoken');
    fetch(`index/message/${ad_id}`, {
        method: 'POST',
        headers: {'X-CSRFToken': csrftoken},
        body: JSON.stringify({
            "text": text
            })
        })
        .then(response => response.json())
        .then(data => {
            // Reload section to show new message sent.
            message_status = document.querySelector("#message-status");
                message_status.innerHTML = data.message;
        });
}

function ordering(order) {
    // Update and load url with sorting parameter
    const new_url = new URL(window.location.href);
    const params = new URLSearchParams(new_url.search);
    params.set('sorting', order); // Add sorting method as GET parameter.
    new_url.search = params.toString();
    window.location.href = new_url.toString();
}
