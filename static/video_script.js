const chatInput = document.querySelector("#chat-input");
const sendButton = document.querySelector("#send-btn");
const chatContainer = document.querySelector(".chat-container");
const themeButton = document.querySelector("#theme-btn");
const deleteButton = document.querySelector("#delete-btn");
const userImageUrl = document.querySelector("#user-image-data").getAttribute("data-image-url");
const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
let userText = null;

const loadDataFromLocalstorage = () => {
    const themeColor = localStorage.getItem("themeColor");

    document.body.classList.toggle("light-mode", themeColor === "light_mode");
    themeButton.innerText = document.body.classList.contains("light-mode") ? "dark_mode" : "light_mode";

    const defaultText = `<div class="default-text">
                            <h1>VisioWave</h1>
                            <p>Start generating Image and videos with a simple prompt!</p>
                        </div>`;

    chatContainer.innerHTML = localStorage.getItem("all-chats") || defaultText;
    document.getElementById('generated-video').src = '';
    document.getElementById('generated-video').style.display = 'none';

    document.getElementById('download-link').style.display = 'none';
    chatContainer.scrollTo(0, chatContainer.scrollHeight);
};

const createChatElement = (content, className) => {
    const chatDiv = document.createElement("div");
    chatDiv.classList.add("chat", className);
    chatDiv.innerHTML = content;
    return chatDiv;
};

const clearExistingContent = () => {
    document.getElementById('generated-video').src = '';
    document.getElementById('generated-video').style.display = 'none';
    document.getElementById('download-link').href = '#';
    document.getElementById('download-link').style.display = 'none';
    chatContainer.innerHTML = '';
};

/**
 * Displays a video file in the given video element.
 *
 * @param {Blob} videoFile - The video file blob to be displayed.
 * @param {HTMLVideoElement} videoEl - The video element where the video will be displayed.
 */
function displayVideo(videoFile, videoEl) {
    // Preconditions
    if (!(videoFile instanceof Blob)) throw new Error('`videoFile` must be a Blob or File object.');
    if (!(videoEl instanceof HTMLVideoElement)) throw new Error('`videoEl` must be a <video> element.');

    // Create a new object URL for the video blob
    const newObjectUrl = URL.createObjectURL(videoFile);

    // Revoke the old object URL if it exists
    const oldObjectUrl = videoEl.currentSrc;
    if (oldObjectUrl && oldObjectUrl.startsWith('blob:')) {
        videoEl.src = ''; // Un-set the src property before revoking the object URL.
        URL.revokeObjectURL(oldObjectUrl);
    }

    // Set the new object URL and load the video
    videoEl.src = newObjectUrl;
    videoEl.load();
}

const generateVideo = async (prompt) => {
    const formData = new FormData();
    formData.append('text', prompt);

    document.getElementById('status-message').innerText = 'Generating video...';
    document.getElementById('status-message').style.display = 'block';

    try {
        const response = await fetch('/generate_video', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            },
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const blob = await response.blob();
        const videoElement = document.getElementById('generated-video');

        // Use the displayVideo function to handle the Blob
        displayVideo(blob, videoElement);

        // Show download link
        const downloadLink = document.getElementById('download-link');
        downloadLink.href = URL.createObjectURL(blob);
        downloadLink.style.display = 'block';
        downloadLink.download = 'generated_video.mp4';

        document.getElementById('status-message').style.display = 'none';
    } catch (error) {
        document.getElementById('status-message').innerText = `Error: ${error.message}`;
        console.error('Error generating video:', error);
    }
};

const handleOutgoingChat = () => {
    userText = chatInput.value.trim();
    if (!userText) return;

    chatInput.value = "";
    chatInput.style.height = `${initialInputHeight}px`;

    clearExistingContent(); // Clear existing content before generating new video

    const html = `<div class="chat-content">
                    <div class="chat-details">
                        <img src="${userImageUrl}" alt="user-img">
                        <p>${userText}</p>
                    </div>
                  </div>`;

    const outgoingChatDiv = createChatElement(html, "outgoing");
    chatContainer.querySelector(".default-text")?.remove();
    chatContainer.appendChild(outgoingChatDiv);
    chatContainer.scrollTo(0, chatContainer.scrollHeight);

    generateVideo(userText);
};

deleteButton.addEventListener("click", () => {
    if (confirm("Are you sure you want to delete all the chats?")) {
        localStorage.removeItem("all-chats");
        loadDataFromLocalstorage();
    }
});

themeButton.addEventListener("click", () => {
    document.body.classList.toggle("light-mode");
    localStorage.setItem("themeColor", document.body.classList.contains("light-mode") ? "light_mode" : "dark_mode");
    themeButton.innerText = document.body.classList.contains("light-mode") ? "dark_mode" : "light_mode";
});

const initialInputHeight = chatInput.scrollHeight;

chatInput.addEventListener("input", () => {   
    chatInput.style.height = `${initialInputHeight}px`;
    chatInput.style.height = `${chatInput.scrollHeight}px`;
});

chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey && window.innerWidth > 800) {
        e.preventDefault();
        handleOutgoingChat();
    }
});

loadDataFromLocalstorage();
sendButton.addEventListener("click", handleOutgoingChat);
