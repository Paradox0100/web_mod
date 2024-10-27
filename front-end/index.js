function submit() {
    var url = document.getElementById("urlInput").value;
    if (!isValidURL(url)) {
        alert("Please enter a valid URL");
    } else {
        toServer(url);
    }
    console.log(url);
}

function isValidURL(url) {
    try {
        new URL(url);
        return true; // If no error is thrown, the URL is valid
    } catch {
        return false; // If an error is thrown, the URL is invalid
    }
}

async function toServer(inputData) {
    try {
        const response = await fetch('http://127.0.0.1:5000/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ data: inputData }), // Sending data as JSON
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        // Determine content type and handle accordingly
        const contentType = response.headers.get('Content-Type');

        if (contentType.includes('text/html')) {
            const newHtml = await response.text(); // Get the HTML response as text
            document.open();
            document.write(newHtml);
            document.close();
        } else if (contentType.includes('image/png') || contentType.includes('image/jpeg') || contentType.includes('image/gif')) {
            const blob = await response.blob(); // Get the image response as a blob
            const imgElement = document.createElement('img');
            imgElement.src = URL.createObjectURL(blob);
            document.body.appendChild(imgElement); // Append image to body
        } else if (contentType.includes('application/json')) {
            const jsonResponse = await response.json();
            console.log(jsonResponse); // Handle JSON response
        } else if (contentType.includes('text/css')) {
            const cssText = await response.text();
            const styleElement = document.createElement('style');
            styleElement.textContent = cssText; // Add CSS dynamically
            document.head.appendChild(styleElement);
        } else if (contentType.includes('application/javascript')) {
            const jsText = await response.text();
            const scriptElement = document.createElement('script');
            scriptElement.textContent = jsText; // Add JS dynamically
            document.body.appendChild(scriptElement);
        } else {
            const text = await response.text();
            console.log(text); // Handle other text responses
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error sending data: ' + error.message);
    }
}