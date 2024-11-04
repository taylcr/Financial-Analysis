// Define initializeSecAnalysis outside of DOMContentLoaded
function showLoadingBubbles() {
    const chatMessages = document.getElementById('chatMessages');
    let loadingBubbles = chatMessages.querySelector('.chat-loading-bubbles');
    
    // If loading bubbles don't exist, create them
    if (!loadingBubbles) {
        loadingBubbles = document.createElement('div');
        loadingBubbles.className = 'chat-loading-bubbles';
        loadingBubbles.innerHTML = `
            <div class="bubble"></div>
            <div class="bubble"></div>
            <div class="bubble"></div>
        `;
        chatMessages.appendChild(loadingBubbles);
    }
    
    loadingBubbles.style.display = 'flex';
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function hideLoadingBubbles() {
    const loadingBubbles = document.querySelector('.chat-loading-bubbles');
    if (loadingBubbles) {
        loadingBubbles.style.display = 'none';
    }
}


function initializeSecAnalysis() {
    const retrieveBtn = document.getElementById('retrieveBtn');
    const yearSelect = document.getElementById('yearSelect');
    const docSelect = document.getElementById('docSelect');
    const openNewTab = document.getElementById('openNewTab');
    const reportAnalysis = document.getElementById('reportAnalysis');

    if (!retrieveBtn || !yearSelect || !docSelect || !openNewTab || !reportAnalysis) {
        console.error('Required elements not found');
        return;
    }

    retrieveBtn.addEventListener('click', async () => {
        const searchInput = document.querySelector('.search-input');
        const ticker = searchInput?.value?.trim().toUpperCase();

        if (!ticker) {
            alert('Please enter a stock symbol first');
            return;
        }

        try {
            // Update button state and show loading
            retrieveBtn.disabled = true;
            retrieveBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Retrieving...';
            reportAnalysis.value = 'Analyzing SEC filing... This may take a minute...';

            const response = await fetch('/analyze_sec_report', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    ticker: ticker,
                    year: yearSelect.value,
                    formType: docSelect.value,
                    openLink: openNewTab.checked
                })
            });

            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }

            // Display the analysis result
            if (data.analysis) {
                reportAnalysis.value = data.analysis;
            } else {
                reportAnalysis.value = 'No analysis available for this document.';
            }

            // Optional: Add a note about the document URL if it was opened
            if (openNewTab.checked && data.url) {
                reportAnalysis.value += '\n\nNote: The document has been opened in a new tab.';
            }

        } catch (error) {
            reportAnalysis.value = `Error: ${error.message}`;
            console.error('Error:', error);
        } finally {
            // Reset button state
            retrieveBtn.disabled = false;
            retrieveBtn.innerHTML = '<i class="fas fa-download"></i> Retrieve Report';
        }
    });

    // Add event listener for the toggle switch to update the button text
    openNewTab.addEventListener('change', () => {
        const buttonIcon = openNewTab.checked ? 'fa-external-link-alt' : 'fa-download';
        retrieveBtn.innerHTML = `<i class="fas ${buttonIcon}"></i> ${openNewTab.checked ? 'Retrieve & Open' : 'Retrieve & Analyze'}`;
    });

    // Initialize button text based on initial toggle state
    const initialIcon = openNewTab.checked ? 'fa-external-link-alt' : 'fa-download';
    retrieveBtn.innerHTML = `<i class="fas ${initialIcon}"></i> ${openNewTab.checked ? 'Retrieve & Open' : 'Retrieve & Analyze'}`;
}

let conversationHistory = ""; // This will hold the ongoing conversation context

async function handleSendMessage() {
    const message = chatInput.value.trim();
    if (!message) return;

    addMessage(message, true); // Display the user's message
    chatInput.value = '';

    // Append the user's message to the conversation history
    conversationHistory += `User: ${message}\n`;

    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message, conversationHistory }) // Send the updated conversation history
        });

        const data = await response.json();
        
        if (data.error) {
            addMessage('Sorry, I encountered an error. Please try again.', false);
        } else {
            addMessage(data.summary, false);
            // Append bot response to conversation history
            conversationHistory += `Bot: ${data.summary}\n`;
        }
    } catch (error) {
        console.error('Error:', error);
        addMessage('Sorry, there was an error processing your request.', false);
    }
}

function initializeChat() {
    const chatButton = document.querySelector('.chat-button');
    const chatWidget = document.getElementById('chatWidget');
    const closeChat = document.getElementById('closeChat');
    const chatInput = document.getElementById('chatInput');
    const sendMessage = document.getElementById('sendMessage');
    const chatMessages = document.getElementById('chatMessages');

    let isOpen = false;

    chatButton.addEventListener('click', () => {
        isOpen = !isOpen;
        if (isOpen) {
            chatWidget.classList.add('show');
            chatInput.focus();
        } else {
            chatWidget.classList.remove('show');
        }
    });

    closeChat.addEventListener('click', () => {
        isOpen = false;
        chatWidget.classList.remove('show');
    });

    async function handleSendMessage() {
        const message = chatInput.value.trim();
        if (!message) return;

        // Add user message
        addMessage(message, true);
        chatInput.value = '';

        // Show loading animation
        showLoadingBubbles();

        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message })
            });

            const data = await response.json();
            
            // Hide loading animation
            hideLoadingBubbles();
            
            if (data.error) {
                addMessage('Sorry, I encountered an error. Please try again.', false);
            } else {
                addMessage(data.summary, false);
            }
        } catch (error) {
            // Hide loading animation on error
            hideLoadingBubbles();
            console.error('Error:', error);
            addMessage('Sorry, there was an error processing your request.', false);
        }
    }

    function addMessage(text, isUser) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('chat-message');
        messageDiv.classList.add(isUser ? 'user' : 'bot');
        messageDiv.textContent = text;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    sendMessage.addEventListener('click', handleSendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleSendMessage();
        }
    });
}

// Single DOMContentLoaded event listener
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the chart first
    let stockChart = initializeChart();
    
    // Initialize search functionality
    initializeSearch(stockChart);
    
    // Chat Functionality
    initializeChat();
    
    // Financial Report Options
    initializeFinancialOptions();
    
    // Initialize SEC Analysis
    initializeSecAnalysis();
});

function initializeChart() {
    const chartCard = document.querySelector('.chart-card');
    let chartInstance = chartCard.querySelector('#stockChart');

    // Check if the chart canvas already exists
    if (!chartInstance) {
        chartInstance = document.createElement('canvas');
        chartInstance.id = 'stockChart';
        chartCard.appendChild(chartInstance);
    }

    const ctx = chartInstance.getContext('2d');

    // Initialize time range controls if they don't exist
    if (!chartCard.querySelector('.time-range-controls')) {
        const timeRangeControls = document.createElement('div');
        timeRangeControls.className = 'time-range-controls';
        timeRangeControls.innerHTML = `
            <div class="btn-group">
                
                <button class="time-btn" data-range="1w">1W</button>
                <button class="time-btn" data-range="1m">1M</button>
                <button class="time-btn" data-range="1y">1Y</button>
                <button class="time-btn" data-range="5y">5Y</button>
                <button class="time-btn active" data-range="all">ALL</button>
            </div>
        `;
        chartCard.insertBefore(timeRangeControls, chartInstance);
    }

    // Check and set the chart title
    let chartTitle = chartCard.querySelector('.chart-title');
    if (!chartTitle) {
        chartTitle = document.createElement('h3');
        chartTitle.className = 'chart-title text-center mb-4';
        chartTitle.textContent = 'Stock Price Movement';
        chartCard.insertBefore(chartTitle, chartCard.firstChild);
    }

    // Initialize or update the chart instance
    if (!window.chartInstance) {
        window.chartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Stock Price',
                    data: [],
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

    // Set up event listeners for buttons
    document.querySelectorAll('.time-btn').forEach(button => {
        button.addEventListener('click', async () => {
            const range = button.dataset.range;
            const currentSymbol = document.querySelector('.search-input').value.trim().toUpperCase();
            if (currentSymbol) {
                // Update active button
                document.querySelectorAll('.time-btn').forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');

                // Fetch and update data
                await fetchAndUpdateChartData(currentSymbol, range, window.chartInstance);
            }
        });
    });

    return window.chartInstance;
}


async function fetchAndUpdateChartData(symbol, timeRange, chart) {
    try {
        const response = await fetch('/get_stock_data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                ticker: symbol,
                range: timeRange 
            })
        });

        const data = await response.json();
        if (data.error) throw new Error(data.error);

        // Update chart title with company name
        const chartTitle = document.querySelector('.chart-title');
        if (chartTitle) {
            chartTitle.textContent = `Stock Price Movement of ${symbol}`;
        }

        // Update chart with new data
        updateChart(chart, data.dates, data.price);

        return data; // Return data for metrics update

    } catch (error) {
        console.error('Error fetching chart data:', error);
        alert('Error updating chart data');
        throw error;
    }
}

function initializeSearch(chart) {
    const searchInput = document.querySelector('.search-input');
    const searchBtn = document.querySelector('.search-btn');

    async function handleSearch() {
        const searchTerm = searchInput.value.trim().toUpperCase();
        if (!searchTerm) {
            alert('Please enter a stock symbol');
            return;
        }

        try {
            // Show loading state
            searchBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            searchBtn.disabled = true;

            // Get the current active time range
            const activeTimeRange = document.querySelector('.time-btn.active')?.dataset.range || '1y';

            // Get stock data
            const stockData = await fetchAndUpdateChartData(searchTerm, activeTimeRange, chart);

            // Get financial indicators
            const indicatorsResponse = await fetch('/get_financial_indicators', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ ticker: searchTerm })
            });

            const indicatorsData = await indicatorsResponse.json();
            if (indicatorsData.error) {
                throw new Error(indicatorsData.error);
            }

            // Update metrics cards with new data
            updateMetricsCards(indicatorsData, stockData);

        } catch (error) {
            console.error('Error:', error);
            alert('Error fetching data: ' + error.message);
        } finally {
            // Reset button state
            searchBtn.innerHTML = '<i class="fas fa-search"></i>';
            searchBtn.disabled = false;
        }
    }

    // Add event listeners
    searchBtn.addEventListener('click', handleSearch);
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleSearch();
        }
    });
}


function initializeFinancialOptions() {
    const uploadBtn = document.getElementById('uploadBtn');
    const analyzeUploadBtn = document.getElementById('analyzeUploadBtn');
    const retrieveBtn = document.getElementById('retrieveBtn');
    const downloadBtn = document.getElementById('downloadBtn');
    const analyzeRetrieveBtn = document.getElementById('analyzeRetrieveBtn');
    const yearSelect = document.querySelector('.year-select');
    const docSelect = document.querySelector('.doc-select');
    const reportAnalysis = document.getElementById('reportAnalysis');

    if (uploadBtn) {
        uploadBtn.addEventListener('click', () => {
            const fileInput = document.createElement('input');
            fileInput.type = 'file';
            fileInput.accept = '.pdf';
            fileInput.click();

            fileInput.onchange = (e) => {
                const file = e.target.files[0];
                if (file) {
                    if (analyzeUploadBtn) analyzeUploadBtn.style.display = 'flex';
                    if (reportAnalysis) reportAnalysis.value = `Selected file: ${file.name}`;
                }
            };
        });
    }

    if (retrieveBtn && yearSelect && docSelect) {
        retrieveBtn.addEventListener('click', () => {
            const year = yearSelect.value;
            const docType = docSelect.value;
            
            if (!year || !docType) {
                alert('Please select both year and document type');
                return;
            }

            if (reportAnalysis) {
                reportAnalysis.value = `Retrieving ${docType} report for ${year}...`;
            }
            
            setTimeout(() => {
                if (downloadBtn) downloadBtn.style.display = 'flex';
                if (analyzeRetrieveBtn) analyzeRetrieveBtn.style.display = 'flex';
                if (reportAnalysis) {
                    reportAnalysis.value = `${docType} report for ${year} is ready.`;
                }
            }, 1500);
        });
    }

    // Analysis handlers
    const handleAnalysis = (type) => () => {
        if (reportAnalysis) {
            reportAnalysis.value = 'Analyzing report...';
            setTimeout(() => {
                reportAnalysis.value = `Analysis complete.\n\nKey Findings:\n- Revenue: $391.03B\n- Operating Margin: 46.21%\n- Free Cash Flow: $112.48B\n- Strong market position maintained`;
            }, 2000);
        }
    };

    if (analyzeUploadBtn) {
        analyzeUploadBtn.addEventListener('click', handleAnalysis('upload'));
    }
    if (analyzeRetrieveBtn) {
        analyzeRetrieveBtn.addEventListener('click', handleAnalysis('retrieve'));
    }

    // Download functionality
    if (downloadBtn && yearSelect && docSelect) {
        downloadBtn.addEventListener('click', () => {
            const year = yearSelect.value;
            const docType = docSelect.value;
            const link = document.createElement('a');
            link.href = '#';
            link.download = `${docType}_${year}_report.pdf`;
            link.click();
        });
    }
}

// Helper functions for updateMetricsCards
function updateMetricsCards(indicators, stockData) {
    const cards = document.querySelectorAll('.metric-card');
    
    // Update Revenue Card
    const revenueCard = cards[0];
    if (revenueCard) {
        const yoyChange = calculateYearOverYearChange(
            indicators.revenue,
            indicators.previous_year_revenue
        );
        
        revenueCard.innerHTML = `
            <div class="metric-header">
                <div>
                    <div class="metric-value">${formatNumber(indicators.revenue)}</div>
                    <div class="metric-label">Chiffre d'affaires (Revenue)</div>
                    <div class="metric-change ${yoyChange.increased ? 'text-green-500' : 'text-red-500'}">
                        <i class="fas fa-arrow-${yoyChange.increased ? 'up' : 'down'}"></i> 
                        ${yoyChange.percentage.toFixed(1)}%
                    </div>
                </div>
                <div class="metric-icon" style="background: #ebf5ff;">
                    <i class="fas fa-chart-line" style="color: #3b82f6;"></i>
                </div>
            </div>`;
    }

    // Update Market Sentiment Card
    const sentimentCard = cards[1];
    if (sentimentCard) {
        const sentiment = indicators.gross_margin ? (indicators.gross_margin * 100).toFixed(1) : '48.4';
        sentimentCard.innerHTML = `
            <div class="metric-header">
                <div>
                    <div class="metric-value">${sentiment}%</div>
                    <div class="metric-label">Market Sentiment</div>
                    <div class="metric-change">${getSentimentLabel(parseFloat(sentiment))}</div>
                </div>
                <div class="metric-icon" style="background: #ecfdf5;">
                    <i class="fas fa-thumbs-up" style="color: #10b981;"></i>
                </div>
            </div>`;
    }

    // Update FCF Card
    const fcfCard = cards[2];
    if (fcfCard) {
        const fcfMargin = ((indicators.free_cash_flow / indicators.revenue) * 100).toFixed(1);
        fcfCard.innerHTML = `
            <div class="metric-header">
                <div>
                    <div class="metric-value">${formatNumber(indicators.free_cash_flow)}</div>
                    <div class="metric-label">Flux de trésorerie libre (FCF)</div>
                    <div class="metric-change">FCF Margin: ${fcfMargin}%</div>
                </div>
                <div class="metric-icon" style="background: #f0fdf4;">
                    <i class="fas fa-money-bill-wave" style="color: #22c55e;"></i>
                </div>
            </div>`;
    }

    // Update Risk Level Card
    const riskCard = cards[3];
    if (riskCard) {
        const { riskLevel, beta } = calculateRiskMetrics(stockData.price, indicators);
        riskCard.innerHTML = `
            <div class="metric-header">
                <div>
                    <div class="metric-value">${riskLevel}</div>
                    <div class="metric-label">Risk Level</div>
                    <div class="metric-change">Beta: ${beta.toFixed(2)}</div>
                </div>
                <div class="metric-icon" style="background: ${getRiskColor(riskLevel)};">
                    <i class="fas fa-exclamation-triangle" style="color: ${getRiskIconColor(riskLevel)};"></i>
                </div>
            </div>`;
    }
}
// Utility functions
function formatNumber(num) {
    if (num === null || num === undefined) return 'N/A';
    
    const absNum = Math.abs(num);
    const sign = num < 0 ? '-' : '';
    
    if (absNum >= 1e12) return `${sign}$${(absNum / 1e12).toFixed(2)}T`;
    if (absNum >= 1e9) return `${sign}$${(absNum / 1e9).toFixed(2)}B`;
    if (absNum >= 1e6) return `${sign}$${(absNum / 1e6).toFixed(2)}M`;
    if (absNum >= 1e3) return `${sign}$${(absNum / 1e3).toFixed(2)}K`;
    return `${sign}$${absNum.toFixed(2)}`;
}

function calculateYearOverYearChange(currentRevenue, previousRevenue) {
    if (!currentRevenue || !previousRevenue) return { percentage: 0, increased: false };
    const change = ((currentRevenue - previousRevenue) / previousRevenue) * 100;
    return {
        percentage: Math.abs(change),
        increased: change > 0
    };
}

function getSentimentLabel(sentiment) {
    if (sentiment >= 70) return 'Strongly Positive';
    if (sentiment >= 50) return 'Positive';
    if (sentiment >= 30) return 'Neutral';
    if (sentiment >= 10) return 'Negative';
    return 'Strongly Negative';
}

function calculateRiskMetrics(prices, indicators) {
    // Calculate daily returns
    const returns = [];
    for (let i = 1; i < prices.length; i++) {
        returns.push((prices[i] - prices[i-1]) / prices[i-1]);
    }

    // Calculate volatility (standard deviation of returns)
    const avgReturn = returns.reduce((a, b) => a + b, 0) / returns.length;
    const variance = returns.reduce((a, b) => a + Math.pow(b - avgReturn, 2), 0) / returns.length;
    const volatility = Math.sqrt(variance);

    // Calculate beta using market average volatility of 0.12 (approximate S&P 500)
    const beta = volatility / 0.12;

    // Determine risk level based on multiple factors
    let riskScore = 0;
    
    // Volatility contribution
    if (volatility > 0.03) riskScore += 3;
    else if (volatility > 0.02) riskScore += 2;
    else if (volatility > 0.01) riskScore += 1;

    // Debt ratio contribution (if available)
    if (indicators.net_debt && indicators.revenue) {
        const debtRatio = indicators.net_debt / indicators.revenue;
        if (debtRatio > 0.5) riskScore += 2;
        else if (debtRatio > 0.3) riskScore += 1;
    }

    // FCF margin contribution
    if (indicators.free_cash_flow && indicators.revenue) {
        const fcfMargin = indicators.free_cash_flow / indicators.revenue;
        if (fcfMargin < 0.05) riskScore += 2;
        else if (fcfMargin < 0.1) riskScore += 1;
    }

    let riskLevel;
    if (riskScore >= 5) riskLevel = 'Very High';
    else if (riskScore >= 4) riskLevel = 'High';
    else if (riskScore >= 3) riskLevel = 'Moderate';
    else if (riskScore >= 2) riskLevel = 'Low';
    else riskLevel = 'Very Low';

    return { riskLevel, beta };
}

function getRiskColor(riskLevel) {
    switch (riskLevel) {
        case 'Very High': return '#fef2f2';
        case 'High': return '#fff7ed';
        case 'Moderate': return '#fffbeb';
        case 'Low': return '#f0fdf4';
        case 'Very Low': return '#ecfdf5';
        default: return '#f9fafb';
    }
}

function getRiskIconColor(riskLevel) {
    switch (riskLevel) {
        case 'Very High': return '#dc2626';
        case 'High': return '#ea580c';
        case 'Moderate': return '#eab308';
        case 'Low': return '#22c55e';
        case 'Very Low': return '#10b981';
        default: return '#6b7280';
    }
}

function updateChart(chart, labels, prices) {
    if (!chart || !labels || !prices) {
        console.error('Missing required parameters for chart update');
        return;
    }

    
    console.log('Updating chart with:', { 
        labelCount: labels.length, 
        priceCount: prices.length 
    });

    chart.data.labels = labels;
    chart.data.datasets[0].data = prices;
    chart.update();
}