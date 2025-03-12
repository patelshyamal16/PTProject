document.addEventListener("DOMContentLoaded", () => {
    showContent('Dashboard');

    renderMediaCollection("Movie");
    renderMediaCollection("TV Show");
    renderMediaCollection("userMovie");
    renderMediaCollection("userTV Show");
    updateTotalProgress();
});

function filterItems(collectionType, filterType) {
    const collectionMap = {
        'movie': 'movie-collection',
        'tvshow': 'tvshow-collection',
        'userMovie': 'User_movie-collection',
        'userTV Show': 'User_tvshow-collection'
    };

    const collection = document.getElementById(collectionMap[collectionType]);

    if (!collection) {
        console.error('Container not found:', collectionMap[collectionType]);
        return;
    }

    const items = collection.getElementsByClassName('item');

    for (let item of items) {
        item.style.display = 'block'; // Reset display style
    }

    if (filterType === 'genre' || filterType === 'title' || filterType === 'released') {
        const filterValue = prompt(`Enter ${filterType} to filter by:`).toLowerCase();

        for (let item of items) {
            const itemData = item.getAttribute(`data-${filterType}`).toLowerCase();
            if (!itemData.includes(filterValue)) {
                item.style.display = 'none';
            }
        }
    }
}

function showContent(section) {
    const buttons = document.querySelectorAll('.sidebar button');
    const clickedButton = document.querySelector(`.sidebar .${section.toLowerCase()}`);

    buttons.forEach(button => {
        if (button !== clickedButton) {
            button.classList.remove('active');
        }
    });

    clickedButton.classList.add('active');

    buttons.forEach(button => {
        button.classList.add('loading');
        button.innerHTML = `${button.innerHTML} <span class="loading-spinner"></span>`; // Add spinner
    });

    setTimeout(() => {
        const sections = document.querySelectorAll('.content-section');
        sections.forEach(sec => sec.classList.remove('active'));

        document.getElementById(`${section}-content`).classList.add('active');

        buttons.forEach(button => {
            button.classList.remove('loading');
            button.innerHTML = button.innerHTML.replace(/<span class="loading-spinner"><\/span>/, ''); // Remove spinner
        });
    }, 1000); // Simulating a 1-second loading delay; adjust as needed
}

function addToCollection(show_id) {
    fetch(`/add_to_collection/${show_id}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(data => {
        const statusElement = document.getElementById(`status-${show_id}`);
        if (data.message) {
            statusElement.textContent = data.message;
            statusElement.className = "success-message"; // Set class for styling
            renderMediaCollection("userMovie");
            renderMediaCollection("userTV Show");
            updateTotalProgress();
        } else if (data.error) {
            statusElement.textContent = data.error;
            statusElement.className = "error-message"; // Set class for styling
        }
    })
    .catch(error => {
        console.error('Error:', error);
        const statusElement = document.getElementById(`status-${show_id}`);
        statusElement.textContent = "An error occurred.";
        statusElement.className = "error-message"; // Set class for styling
    });
}

function removeFromCollection(show_id) {
    fetch(`/remove_from_userCollection/${show_id}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(data => {
        const statusElement = document.getElementById(`delete-${show_id}`);
        if (data.message) {
            statusElement.textContent = data.message;
            statusElement.className = "success-message"; // Set class for styling
            renderMediaCollection("userMovie");
            renderMediaCollection("userTV Show");
            updateTotalProgress();
        } else if (data.error) {
            statusElement.textContent = data.error;
            statusElement.className = "error-message"; // Set class for styling
        }
    })
    .catch(error => {
        console.error('Error:', error);
        const statusElement = document.getElementById(`delete-${show_id}`);
        statusElement.textContent = "An error occurred.";
        statusElement.className = "error-message"; // Set class for styling
    });
}

function updateProgress(content_id) {
    fetch(`/update_progress/${content_id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(data => {
        updateTotalProgress();
        const progressElement = document.getElementById(`progress-${content_id}`);
        if (data.new_progress !== undefined) {
            // Map progress values to text
            let progressText;
            switch(data.new_progress) {
                case 0:
                    progressText = "Not yet started";
                    break;
                case 1:
                    progressText = "In-progress";
                    break;
                case 2:
                    progressText = "Completed";
                    break;
            }
            progressElement.textContent = `Progress: ${progressText}`;
        } else if (data.error) {
            progressElement.textContent = "Error updating progress.";
            console.error(data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function renderMediaCollection(mediaType) {
    const containerMap = {
        'Movie': 'movie-collection',
        'TV Show': 'tvshow-collection',
        'userMovie': 'User_movie-collection',
        'userTV Show': 'User_tvshow-collection'
    };

    const container = document.getElementById(containerMap[mediaType]);

    if (!container) {
        console.error('Container not found:', containerMap[mediaType]);
        return;
    }

    container.innerHTML = '';

    const ol = document.createElement("ol");

    try {
        fetch('/update_collection', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(response => response.json())
        .then(data => {
            const collectionMap = {
                'Movie': data.movies,
                'TV Show': data.tv_shows,
                'userMovie': data.userMovies,
                'userTV Show': data.userTv_shows
            };

            const collection = collectionMap[mediaType];
            console.log("start to print")
            collection.forEach(item => {
                const itemDiv = document.createElement("div");
                itemDiv.className = "item";
                itemDiv.dataset.genre = item.genre || "";
                itemDiv.dataset.title = item.title;
                itemDiv.dataset.released = item.releaseYear || "";

                const listItem = document.createElement("li");

                const durationOrSeasonLabel = item.type === 'Movie'  ? 'Duration' : 'Season';
                const durationOrSeasonValue = item.type === 'Movie' ? `${item.duration} mins` : `${item.season}`;

                listItem.innerHTML = `
                    <strong>Title:</strong> ${item.title} (${item.releaseYear || "N/A"})<br>
                    <strong>Rating, ${durationOrSeasonLabel}:</strong> ${item.rating || "N/A"}, ${durationOrSeasonValue}<br>
                    <strong>GENRES:</strong> ${item.genre}<br>
                    <strong>DATE ADDED:</strong> ${item.dateAdded}<br>
                    <strong>COUNTRIES:</strong> ${item.country}<br><br>
                    <strong>DESCRIPTION:</strong> ${item.description}<br>
                    <strong>CASTS:</strong> ${item.cast}<br>
                    <strong>DIRECTORS:</strong> ${item.director}<br>
                `;

                if (mediaType === 'userMovie' || mediaType === 'userTV Show') {
                    const button = document.createElement("button");
                    button.textContent = "Progress";
                    button.onclick = () => updateProgress(item.show_id);

                    const statusSpan = document.createElement("span");
                    statusSpan.id = `progress-${item.show_id}`;
                    statusSpan.className = "progressStatus";

                    const button2 = document.createElement("button");
                    button2.textContent = "Remove from Collection";
                    button2.onclick = () => removeFromCollection(item.show_id);

                    const statusSpan2 = document.createElement("span");
                    statusSpan2.id = `delete-${item.show_id}`;
                    statusSpan2.className = "deleteStatus";

                    listItem.appendChild(button);
                    listItem.appendChild(statusSpan);
                    listItem.appendChild(button2);
                    listItem.appendChild(statusSpan2);
                } else {
                    const button = document.createElement("button");
                    button.textContent = "Add to Collection";
                    button.onclick = () => addToCollection(item.show_id);
                    listItem.appendChild(button);

                    const statusSpan = document.createElement("span");
                    statusSpan.id = `status-${item.show_id}`;
                    statusSpan.className = "status-message";
                    listItem.appendChild(statusSpan);
                }

                itemDiv.appendChild(listItem);
                ol.appendChild(itemDiv);
            });

            container.appendChild(ol);
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });
    } catch (error) {
        console.error('Error fetching data:', error);
    }
}

function updateTotalProgress() {
    fetch('/total_progress', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(data => {
        if (data.movietotal_progress !== undefined) {
            const progressBar = document.getElementById("movietotal-progress-bar");
            progressBar.style.width = `${data.movietotal_progress}%`;
            progressBar.textContent = `${Math.round(data.movietotal_progress)}% Complete`;
        } 
        if (data.tvshowtotal_progress !== undefined) {
            const progressBar = document.getElementById("tvshowtotal-progress-bar");
            progressBar.style.width = `${data.tvshowtotal_progress}%`;
            progressBar.textContent = `${Math.round(data.tvshowtotal_progress)}% Complete`;
        } else if (data.error) {
            console.error("Error:", data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}