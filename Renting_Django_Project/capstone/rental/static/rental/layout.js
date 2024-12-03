function getCities(country) {
    // API documentation: https://documenter.getpostman.com/view/1134062/T1LJjU52#2e131a94-a28e-4cfe-95fe-d10c0e40eae7
    return fetch("https://countriesnow.space/api/v0.1/countries/cities", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json' // Added to indicate that the request body contains JSON data. Get error without that line.
        },
        body: JSON.stringify({
            "country": country
        }),
        redirect: 'follow'
    })
    .then(response => response.json())
    .then(data => {
        return data.data; // Return the data for further usage
    });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
