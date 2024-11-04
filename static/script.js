document.addEventListener('DOMContentLoaded', function() {
    // Chart Initialization
    initializeChart();
    
    // Chat Functionality
    initializeChat();
    
    // Financial Report Options
    initializeFinancialOptions();
    
    // Search Functionality
    initializeSearch();
});


function initializeChart() {
    const chatButton = document.querySelector('.chat-button');
    const chatWidget = document.getElementById('chatWidget');
    const closeChat = document.getElementById('closeChat');
    const chatInput = document.getElementById('chatInput');
    const sendMessage = document.getElementById('sendMessage');
    const chatMessages = document.getElementById('chatMessages');


    const ctx = document.getElementById('stockChart').getContext('2d');
    
    let isOpen = false;

    // Upload functionality
    uploadBtn.addEventListener('click', () => {
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = '.pdf';
        fileInput.click();

        fileInput.onchange = (e) => {
            const file = e.target.files[0];
            if (file) {
                analyzeUploadBtn.style.display = 'flex';
                reportAnalysis.value = `Selected file: ${file.name}`;
            }
        };
    });

     // Retrieve functionality
     retrieveBtn.addEventListener('click', () => {
        const year = yearSelect.value;
        const docType = docSelect.value;
        
        if (!year || !docType) {
            alert('Please select both year and document type');
            return;
        }

        reportAnalysis.value = `Retrieving ${docType} report for ${year}...`;
        
        // Simulate retrieval
        setTimeout(() => {
            downloadBtn.style.display = 'flex';
            analyzeRetrieveBtn.style.display = 'flex';
            reportAnalysis.value = `${docType} report for ${year} is ready.`;
        }, 1500);
    });
     // Analysis functionality
     function handleAnalysis(type) {
        return () => {
            reportAnalysis.value = 'Analyzing report...';
            setTimeout(() => {
                reportAnalysis.value = `Analysis complete.\n\nKey Findings:\n- Revenue: $391.03B\n- Operating Margin: 46.21%\n- Free Cash Flow: $112.48B\n- Strong market position maintained`;
            }, 2000);
        };
    }

    analyzeUploadBtn.addEventListener('click', handleAnalysis('upload'));
    analyzeRetrieveBtn.addEventListener('click', handleAnalysis('retrieve'));

    // Download functionality
    downloadBtn.addEventListener('click', () => {
        const year = yearSelect.value;
        const docType = docSelect.value;
        const link = document.createElement('a');
        link.href = '#';
        link.download = `${docType}_${year}_report.pdf`;
        link.click();
    });
    // Chat toggle functionality

    chatButton.addEventListener('click', () => {
        isOpen = !isOpen;
        if (isOpen) {
            chatWidget.classList.add('show');
            chatInput.focus(); // Focus on input when opened
        } else {
            chatWidget.classList.remove('show');
        }
    });

    function showTypingIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'typing-indicator';
        indicator.innerHTML = `
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        `;
        chatMessages.appendChild(indicator);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return indicator;
    }

    closeChat.addEventListener('click', (e) => {
        e.stopPropagation(); // Prevent event from bubbling to chatButton
        isOpen = false;
        chatWidget.classList.remove('show');
    });

    // Generate sample data
    const dates = Array.from({length: 20}, (_, i) => {
        const date = new Date();
        date.setDate(date.getDate() - (19 - i));
        return date.toLocaleDateString();
    });
    
    const prices = Array.from({length: 20}, () => 200 + Math.random() * 50);

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: 'Stock Price',
                data: prices,
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
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
                    display: false
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
                        callback: value => `$${value.toFixed(2)}`
                    }
                }
            }
        }
    });
}

function initializeChat() {
    const chatButton = document.querySelector('.chat-button');
    const chatWidget = document.getElementById('chatWidget');
    const closeChat = document.getElementById('closeChat');
    const chatInput = document.getElementById('chatInput');
    const sendMessage = document.getElementById('sendMessage');
    const chatMessages = document.getElementById('chatMessages');

    chatButton.addEventListener('click', () => {
        chatWidget.classList.add('active');
    });

    closeChat.addEventListener('click', () => {
        chatWidget.classList.remove('active');
    });

    function addMessage(message, isUser) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('chat-message');
        messageDiv.classList.add(isUser ? 'user' : 'bot');
        messageDiv.textContent = message;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function handleSendMessage() {
        const message = chatInput.value.trim();
        if (!message) return;

        addMessage(message, true);
        chatInput.value = '';

        // Simulate bot response (replace with actual API call)
        setTimeout(() => {
            addMessage("I'm analyzing the financial data. Here's what I found...", false);
        }, 1000);
    }

    sendMessage.addEventListener('click', handleSendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleSendMessage();
        }
    });
}


function initializeFinancialOptions() {
    const uploadBtn = document.getElementById('uploadBtn');
    const retrieveBtn = document.getElementById('retrieveBtn');
    const downloadBtn = document.getElementById('downloadBtn');
    const yearSelect = document.querySelector('.year-select');
    const reportAnalysis = document.getElementById('reportAnalysis');

    uploadBtn.addEventListener('click', () => {
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = '.pdf';
        fileInput.click();

        fileInput.onchange = (e) => {
            const file = e.target.files[0];
            if (file) {
                reportAnalysis.value = `Analyzing ${file.name}...`;
                setTimeout(() => {
                    reportAnalysis.value = `Analysis of ${file.name}:\n\nKey Findings:\n- Strong revenue growth of 15% YoY\n- Operating margin improved by 2.5%\n- Healthy cash flow position\n- Debt levels within acceptable range`;
                }, 2000);
            }
        };
    });

    retrieveBtn.addEventListener('click', () => {
        const year = yearSelect.value;
        if (year) {
            reportAnalysis.value = `Retrieving report for ${year}...`;
            setTimeout(() => {
                reportAnalysis.value = `Analysis of ${year} Annual Report:\n\nKey Findings:\n- Revenue: $391.03B\n- Operating Margin: 46.21%\n- Free Cash Flow: $112.48B\n- Strong market position maintained`;
            }, 1500);
        } else {
            alert('Please select a year');
        }
    });

    downloadBtn.addEventListener('click', () => {
        const link = document.createElement('a');
        link.href = '#';
        link.download = 'financial_report.pdf';
        link.click();
    });
}

function initializeSearch() {
    const searchInput = document.querySelector('.search-input');
    const searchBtn = document.querySelector('.search-btn');

    function handleSearch() {
        const searchTerm = searchInput.value.trim();
        if (searchTerm) {
            console.log('Searching for:', searchTerm);
            // Add your search implementation here
        }
    }

    searchBtn.addEventListener('click', handleSearch);
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleSearch();
        }
    });
}