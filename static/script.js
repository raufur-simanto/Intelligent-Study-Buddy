let currentAudio = null;

async function uploadFile() {
    const fileInput = document.getElementById('audioFile');
    const file = fileInput.files[0];
    const status = document.getElementById('status');
    const actions = document.getElementById('actions');
    const output = document.getElementById('output');

    if (!file) {
        status.innerText = 'No file selected';
        console.log('No file selected');
        return;
    }

    try {
        status.innerText = 'Requesting pre-signed URL...';
        console.log('Requesting pre-signed URL for:', file.name);

        const res = await fetch('/get-presigned-url', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filename: file.name })
        });

        const data = await res.json();
        console.log('Presigned URL response:', data);

        if (!res.ok) {
            throw new Error(`Presigned URL request failed: ${data.error || res.status}`);
        }

        const uploadRes = await fetch(data.url, {
            method: 'PUT',
            body: file,
            headers: { 'Content-Type': 'audio/mpeg' }
        });

        if (uploadRes.ok) {
            console.log('Upload successful:', uploadRes.status);
            status.innerText = 'Upload successful!';
            actions.classList.remove('hidden');
            output.classList.remove('hidden');
        } else {
            const errorText = await uploadRes.text();
            console.error('Upload failed:', uploadRes.status, errorText);
            throw new Error('Upload failed. See console for details.');
        }

    } catch (err) {
        console.error('Upload error:', err);
        status.innerText = `Error: ${err.message}`;
    }
}

async function getSummary() {
    const status = document.getElementById('status');
    const output = document.getElementById('output');
    const fileInput = document.getElementById('audioFile');

    // Check if any file is selected
    if (!fileInput.files || fileInput.files.length === 0) {
        alert('Please upload a file first!');
        return;
    }

    const filename = fileInput.files[0].name;
    // const filename = '27bf-f44a-451a-a75c-f54f8c216891.mp3'

    if (!filename) {
        alert('Please upload a file first!');
        return;
    }

    try {
        status.innerText = 'Fetching summary...';
        const res = await fetch('/get-summary', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filename })
        });

        const data = await res.json();
        if (res.ok) {
            status.innerText = 'Summary received!';
            output.innerHTML = `<h3>Summary</h3><p id="summaryText">${data.summary}</p>`;
        } else {
            throw new Error(data.error || 'Failed to get summary');
        }
    } catch (err) {
        console.error(err);
        status.innerText = `Error: ${err.message}`;
    }
}


async function getQuiz() {
    const status = document.getElementById('status');
    const output = document.getElementById('output');
    // const quizSection = document.getElementById('quizSection');
    const summaryText = document.getElementById('summaryText')?.innerText;

    if (!summaryText) {
        alert('Please fetch the summary first!');
        return;
    }

    try {
        status.innerText = 'Generating quiz...';
        const res = await fetch('/generate-quiz', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ summary: summaryText })
        });

        const data = await res.json();
        if (!res.ok) {
            throw new Error(data.error || 'Failed to generate quiz');
        }

        status.innerText = 'Quiz generated!';
        
        // Update the quiz section with the questions
        output.innerHTML = `<h3>Quiz Questions</h3><ul>${data.quiz.map(q => `<li>${q}</li>`).join('')}</ul>`;

    } catch (err) {
        console.error(err);
        status.innerText = `Error: ${err.message}`;
    }
}



async function playSummaryAudio() {
    const summaryText = document.getElementById('summaryText')?.innerText;
    const status = document.getElementById('status');

    if (!summaryText) {
        alert('Please fetch the summary first!');
        return;
    }

    try {
        status.innerText = 'Converting summary to speech...';

        const res = await fetch('/text-to-speech', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: summaryText })
        });

        if (res.ok) {
            if (currentAudio) {
                currentAudio.pause();
                currentAudio = null;
            }

            // Create a Blob from the response and play the audio directly
            const audioBlob = await res.blob();  // Get the audio as a Blob
            currentAudio = new Audio(URL.createObjectURL(audioBlob));  // Create a URL for the audio Blob
            currentAudio.play();
            status.innerText = 'Playing summary audio...';
        } else {
            throw new Error('Failed to generate summary audio');
        }
    } catch (err) {
        console.error(err);
        status.innerText = `Error: ${err.message}`;
    }
}



async function playQuizAudio() {
    const outputElement = document.getElementById('output');
    const status = document.getElementById('status');

    // Ensure the quiz was generated before trying to play audio
    if (!outputElement || outputElement.children.length === 0) {
        alert('Please generate the quiz first!');
        return;
    }

    // Collect the quiz questions text from the <ul> inside output
    const quizText = Array.from(outputElement.querySelectorAll('li'))
        .map(li => li.innerText)
        .join(' '); // Join all questions into a single string

    try {
        status.innerText = 'Converting quiz to speech...';

        const res = await fetch('/text-to-speech', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: quizText })
        });

        if (res.ok) {
            // Pause any currently playing audio before starting a new one
            if (currentAudio) {
                currentAudio.pause();
                currentAudio = null;
            }

            // Create a Blob from the response and play the audio directly
            const audioBlob = await res.blob();  // Get the audio as a Blob
            currentAudio = new Audio(URL.createObjectURL(audioBlob));  // Create a URL for the audio Blob
            currentAudio.play();
            status.innerText = 'Playing quiz audio...';
        } else {
            const errorData = await res.json();
            throw new Error(errorData.error || 'Failed to play quiz audio');
        }
    } catch (err) {
        console.error(err);
        status.innerText = `Error: ${err.message}`;
    }
}


// Function to stop the currently playing audio
function stopAudio() {
    const status = document.getElementById('status');
    if (currentAudio) {
        currentAudio.pause();  // Stop the audio
        currentAudio = null;   // Reset the currentAudio to null
        status.innerText = 'Audio stopped.';
    } else {
        status.innerText = 'No audio is currently playing.';
    }
}
