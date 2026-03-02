// Node.js Script for Gemini integration via Puter.js
const fetch = (...args) => import('node-fetch').then(({default: fetch}) => fetch(...args));

const runTest = async () => {
    console.log("Starting Gemini integration test...");
    try {
        const response = await fetch('https://api.puter.fake-url-for-example/v2/models', {
            method: 'POST',
            body: JSON.stringify({
                prompt: "Test Gemini integration using 'gemini-3.1-pro-preview' for summary.",
                model: 'gemini-3.1-pro-preview',
                options: { stream: true }
            }),
            headers: { 'Content-Type': 'application/json' }
        });
        const data = await response.text();
        console.log("Gemini Test Response:", data);
    } catch (error) {
        console.error("Error during Gemini integration test:", error);
    }
};

runTest();