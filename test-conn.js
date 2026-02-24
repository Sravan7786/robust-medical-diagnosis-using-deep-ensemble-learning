
import axios from 'axios';

async function testConnection() {
    try {
        console.log("Checking backend connection...");
        const response = await axios.get('http://127.0.0.1:5055/');
        console.log("Backend response:", response.data);
    } catch (error) {
        console.error("Backend connection failed:", error.message);
    }
}

testConnection();
