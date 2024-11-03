document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const tickerInput = document.getElementById('tickerInput');
    const submitButton = document.getElementById('submitButton');
    const errorMessage = document.getElementById('errorMessage');
    const stockData = document.getElementById('stockData');
    const chatButton = document.getElementById('chatButton');
    const chatWidget = document.getElementById('chatWidget');
    const closeChat = document.getElementById('closeChat');
    const userInput = document.getElementById('userInput');
    const sendMessage = document.getElementById('sendMessage');
    const chatMessages = document.getElementById('chatMessages');

    let currentChart = null;

    // Stock Data Functionality
    submitButton.addEventListener('click', async () => {
        const ticker = tickerInput.value.trim().toUpperCase();
        if (!ticker) {
            errorMessage.textContent = 'Please enter a ticker symbol';
            return;
        }

        // Show loading state
        submitButton.disabled = true;
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
        errorMessage.textContent = '';

        try {
            const response = await fetch('/get_stock_data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ ticker })
            });

            const data = await response.json();
            
            if (data.error) {
                errorMessage.textContent = data.error;
                return;
            }

            // Clear previous chart
            if (currentChart) {
                currentChart.destroy();
            }

            // Create new chart
            const ctx = document.getElementById('stockChart').getContext('2d');
            currentChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.dates,
                    datasets: [{
                        label: ticker,
                        data: data.price,
                        borderColor: '#2563eb',
                        backgroundColor: 'rgba(37, 99, 235, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top'
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false,
                            callbacks: {
                                label: function(context) {
                                    return `$${context.parsed.y.toFixed(2)}`;
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: false,
                            ticks: {
                                callback: function(value) {
                                    return '$' + value.toFixed(2);
                                }
                            }
                        }
                    }
                }
            });

        } catch (error) {
            errorMessage.textContent = 'Error fetching stock data. Please try again.';
        } finally {
            // Reset button state
            submitButton.disabled = false;
            submitButton.innerHTML = 'Get Stock Data';
        }
    });

    // Chat Functionality
    if (chatButton && chatWidget && closeChat) {
        chatButton.addEventListener('click', () => {
            chatWidget.style.display = 'flex';  // Changed from classList
            chatWidget.style.opacity = '1';
            chatWidget.style.transform = 'translateY(0)';
        });

        closeChat.addEventListener('click', () => {
            chatWidget.style.opacity = '0';
            chatWidget.style.transform = 'translateY(20px)';
            setTimeout(() => {
                chatWidget.style.display = 'none';
            }, 300);
        });
    }

    // Send Message Functionality
    async function handleSendMessage() {
        const message = userInput.value.trim();
        if (!message) return;

        // Add user message
        addMessage(message, true);
        userInput.value = '';

        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message })
            });

            const data = await response.json();
            
            // Add bot response
            if (data.error) {
                addMessage('Sorry, I encountered an error. Please try again.', false);
            } else {
                addMessage(data.summary, false);
            }
        } catch (error) {
            addMessage('Sorry, there was an error processing your request.', false);
        }
    }

    // Helper function to add messages
    function addMessage(text, isUser) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');
        messageDiv.classList.add(isUser ? 'user-message' : 'bot-message');
        messageDiv.textContent = text;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Event listeners for sending messages
    if (sendMessage && userInput) {
        sendMessage.addEventListener('click', handleSendMessage);
        
        userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                handleSendMessage();
            }
        });
    }

    // Input validation
    tickerInput.addEventListener('input', (e) => {
        e.target.value = e.target.value.replace(/[^A-Za-z]/g, '').toUpperCase();
    });

    // Handle Enter key in ticker input
    tickerInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            submitButton.click();
        }
    });
});