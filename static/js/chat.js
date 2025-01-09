document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const queryForm = document.getElementById('queryForm');
    const queryInput = document.getElementById('queryInput');
    const messagesContainer = document.getElementById('messagesContainer');
    const loadingOverlay = document.getElementById('loadingOverlay');
    const queryHistory = document.getElementById('queryHistory');
    const errorToast = document.getElementById('errorToast');
    
    // Bootstrap toast initialization
    const toast = new bootstrap.Toast(errorToast);
    
    // Chart instances storage
    let charts = [];
    
    // Auto-resize textarea
    queryInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });

    // Handle form submission
    queryForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const query = queryInput.value.trim();
        if (!query) return;
        
        // Add user message
        addMessage(query, 'user');
        
        // Clear input
        queryInput.value = '';
        queryInput.style.height = 'auto';
        
        // Show loading
        loadingOverlay.style.display = 'flex';
        
        try {
            const response = await sendQuery(query);
            processResponse(response);
        } catch (error) {
            showError(error.message);
        } finally {
            loadingOverlay.style.display = 'none';
        }
    });

    // Handle suggestion buttons
    document.querySelectorAll('.suggestion-btn').forEach(button => {
        button.addEventListener('click', function() {
            queryInput.value = this.dataset.query;
            queryForm.dispatchEvent(new Event('submit'));
        });
    });

    async function sendQuery(query) {
        try {
            // Try the simpler /get endpoint first
            const formData = new FormData();
            formData.append('msg', query);
            
            const response = await fetch('/get', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error('Query failed. Please try again.');
            }
            
            const result = await response.text();
            return {
                success: true,
                data: {
                    result: result,
                    query: query
                }
            };
            
        } catch (error) {
            throw new Error('Failed to send query: ' + error.message);
        }
    }

    // Add message to chat container
    function addMessage(content, type, additionalData = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `d-flex ${type === 'user' ? 'justify-content-end' : 'justify-content-start'} mb-4`;

        let innerHTML = '';
        
        if (type === 'user') {
            innerHTML = `
                <div class="msg_cotainer_send">
                    ${content}
                    <span class="msg_time_send">${new Date().toLocaleTimeString()}</span>
                </div>`;
        } else {
            innerHTML = `
                <div class="img_cont_msg">
                    <img src="" class="rounded-circle user_img_msg">
                </div>
                <div class="msg_cotainer">
                    ${content}
                    <span class="msg_time">${new Date().toLocaleTimeString()}</span>
                </div>`;
        }
        
        messageDiv.innerHTML = innerHTML;
        
        // If there's additional data (like SQL results or charts)
        if (additionalData) {
            if (additionalData.sql) {
                const sqlDiv = document.createElement('div');
                sqlDiv.className = 'sql-result';
                const pre = document.createElement('pre');
                pre.innerHTML = hljs.highlight('sql', additionalData.sql).value;
                sqlDiv.appendChild(pre);
                messageDiv.appendChild(sqlDiv);
            }
            
            if (additionalData.chart) {
                const chartDiv = document.createElement('div');
                chartDiv.className = 'chart-container';
                chartDiv.style.height = '300px';
                messageDiv.appendChild(chartDiv);
                
                // Create chart
                const chartId = 'chart-' + Date.now();
                chartDiv.id = chartId;
                createChart(chartId, additionalData.chart);
            }
        }
        
        messagesContainer.appendChild(messageDiv);
        scrollToBottom();
        
        // Add to history if it's a user message
        if (type === 'user') {
            addToHistory(content);
        }
    }

    // Process the response from the server
    function processResponse(response) {
        if (!response.success) {
            showError(response.error || 'An error occurred');
            return;
        }
        
        // Add bot message
        addMessage(response.data.result, 'bot', {
            sql: response.data.sql,
            chart: response.data.visualization
        });
    }

    // Add query to history
    function addToHistory(query) {
        const historyItem = document.createElement('div');
        historyItem.className = 'history-item';
        historyItem.textContent = query;
        
        // Add click handler to reuse query
        historyItem.addEventListener('click', function() {
            queryInput.value = query;
            queryForm.dispatchEvent(new Event('submit'));
        });
        
        // Add to history container
        if (queryHistory.children.length >= 10) {
            queryHistory.removeChild(queryHistory.firstChild);
        }
        queryHistory.appendChild(historyItem);
    }

    // Create a chart using Chart.js
    function createChart(containerId, chartData) {
        const ctx = document.getElementById(containerId);
        const newChart = new Chart(ctx, {
            type: chartData.type || 'bar',
            data: chartData.data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                ...chartData.options
            }
        });
        
        // Store chart instance for cleanup
        charts.push(newChart);
    }

    // Show error toast
    function showError(message) {
        const toastBody = errorToast.querySelector('.toast-body');
        toastBody.textContent = message;
        toast.show();
    }

    // Scroll chat to bottom
    function scrollToBottom() {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    // Clean up charts when navigating away
    window.addEventListener('beforeunload', function() {
        charts.forEach(chart => chart.destroy());
    });

    // Initialize keyboard shortcuts
    function initKeyboardShortcuts() {
        document.addEventListener('keydown', function(e) {
            // Ctrl/Cmd + Enter to submit
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                e.preventDefault();
                queryForm.dispatchEvent(new Event('submit'));
            }
        });
    }

    // Initialize tooltips
    function initTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // Initialize the application
    function init() {
        initKeyboardShortcuts();
        initTooltips();
        
        // Focus input on load
        queryInput.focus();
        
        // Add welcome message
        addMessage('Hello! How can I help you analyze your database today?', 'bot');
    }

    // Run initialization
    init();
});