const axios = require('axios');

const BASE_URL = 'http://localhost:11434';

// Generate response
async function chat(prompt, model = 'gemma-arabic') {
    const response = await axios.post(`${BASE_URL}/api/generate`, {
        model: model,
        prompt: prompt,
        stream: false
    });
    return response.data.response;
}

// Chat with history
async function chatWithHistory(messages, model = 'gemma-arabic') {
    const response = await axios.post(`${BASE_URL}/api/chat`, {
        model: model,
        messages: messages,
        stream: false
    });
    return response.data.message.content;
}

// Example usage
async function main() {
    console.log('=== Simple Generation ===');
    const result = await chat('What is AI?');
    console.log(result);
    
    console.log('\n=== Chat with History ===');
    const messages = [
        { role: 'user', content: 'Hello, what is your name?' }
    ];
    const chatResult = await chatWithHistory(messages);
    console.log(chatResult);
}

main();
