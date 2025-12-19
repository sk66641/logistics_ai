document.getElementById('date').valueAsDate = new Date();

const form = document.getElementById('prediction-form');
const resultPanel = document.getElementById('result-panel');
const loader = document.getElementById('loader');
const simulateBtn = document.getElementById('simulate-btn');
let chartInstance = null;
let multiCarrierChart = null;
let lastFormData = null;
const API_URL = "https://logistics-ai-c5n9.onrender.com";


form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    loader.style.display = 'block';
    resultPanel.style.display = 'none';

    const formData = {
        Origin: document.getElementById('origin').value,
        Destination: document.getElementById('destination').value,
        Carrier: document.getElementById('carrier').value,
        Date: document.getElementById('date').value,
        ShipmentType: document.getElementById('shipmentType').value,
        ServiceLevel: document.getElementById('serviceLevel').value,
        Mode: document.getElementById('mode').value,
        Priority: document.getElementById('priority').value,
        PackageWeightKg: parseFloat(document.getElementById('packageWeightKg').value || '2'),
        SLAHours: parseInt(document.getElementById('slaHours').value || '48', 10)
    };
    lastFormData = { ...formData };

    try {
        const response = await fetch(`${API_URL}/predict`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        updateDashboard(data);
        
    } catch (error) {
        alert("Error connecting to AI Backend. Make sure it's running!");
        console.error(error);
    } finally {
        loader.style.display = 'none';
        resultPanel.style.display = 'block';
    }
});

function updateDashboard(data) {
    const pred = data.prediction;
    const factors = data.factors;

    // A. Update Text Stats
    document.getElementById('delay-prob').innerText = pred.risk_score + "%";
    document.getElementById('delay-time').innerText = "+" + pred.estimated_delay_hours + " hrs";
    document.getElementById('sla-target').innerText = pred.promised_sla_hours + "h";
    document.getElementById('sla-status').innerText = pred.sla_status;
    document.getElementById('ai-recommendation').innerText = data.recommendation;
    document.getElementById('primary-reason').innerText = factors.primary_reason;

    // Context pills
    document.getElementById('weather-pill').innerText = "🌦 Weather: " + factors.weather_forecast;
    document.getElementById('traffic-pill').innerText = "🚦 Traffic: " + factors.traffic_condition;

    // B. Risk Badge Logic
    const badge = document.getElementById('risk-badge');
    if (pred.risk_level === "High Risk") {
        badge.className = "badge badge-high";
        badge.innerText = "⚠️ High Risk";
        document.getElementById('delay-prob').style.color = "#dc2626"; // Red
    } else if (pred.risk_level === "Medium Risk") {
        badge.className = "badge badge-high";
        badge.innerText = "⚠️ Medium Risk";
        document.getElementById('delay-prob').style.color = "#f97316"; // Orange
    } else {
        badge.className = "badge badge-low";
        badge.innerText = "✅ On Time";
        document.getElementById('delay-prob').style.color = "#16a34a"; // Green
    }

    // C. Render Chart (Explainability)
    renderChart(factors);
}

function renderChart(factors) {
    const ctx = document.getElementById('factorsChart').getContext('2d');
    
    if (chartInstance) {
        chartInstance.destroy();
    }

    let weatherScore = factors.weather_forecast.includes("Rain") ? 80 : 20;
    let trafficScore = factors.traffic_condition.includes("Jam") ? 90 : 30;
    let carrierScore = 40; // Baseline

    chartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Weather Impact', 'Traffic Impact', 'Carrier Risk'],
            datasets: [{
                label: 'Risk Contribution (%)',
                data: [weatherScore, trafficScore, carrierScore],
                backgroundColor: [
                    'rgba(54, 162, 235, 0.7)', // Blue
                    'rgba(255, 99, 132, 0.7)', // Red
                    'rgba(255, 206, 86, 0.7)'  // Yellow
                ],
                borderColor: [
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 99, 132, 1)',
                    'rgba(255, 206, 86, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: { beginAtZero: true, max: 100 }
            },
            plugins: {
                legend: { display: false },
                title: { display: true, text: 'Risk factors' }
            }
        }
    });
}

if (simulateBtn) {
    simulateBtn.addEventListener('click', async () => {
        if (!lastFormData) {
            alert("Run a prediction first, then simulate carriers.");
            return;
        }

        const carriers = ["Delhivery", "Blue Dart", "DTDC", "India Post"];
        const tableBody = document.getElementById('sim-table-body');
        tableBody.innerHTML = `<tr><td colspan="3" style="color:#9ca3af;">Running simulations...</td></tr>`;

        try {
            const requests = carriers.map(carrier => {
                const payload = { ...lastFormData, Carrier: carrier };
                return fetch(`${API_URL}/predict`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                }).then(r => r.json().then(data => ({ carrier, data })));
            });

            const results = await Promise.all(requests);

            // Update table
            tableBody.innerHTML = "";
            const chartLabels = [];
            const chartData = [];

            results.forEach(({ carrier, data }) => {
                const pred = data.prediction;
                const tr = document.createElement('tr');

                const riskTagClass = pred.risk_level === "High Risk" ? "sim-tag sim-tag-high" : "sim-tag sim-tag-low";
                const riskTagText = pred.risk_level === "High Risk" ? "High" : pred.risk_level === "Medium Risk" ? "Medium" : "Low";

                tr.innerHTML = `
                    <td>${carrier}</td>
                    <td>
                        <span class="${riskTagClass}">
                            ${pred.risk_score.toFixed(1)}% • ${riskTagText}
                        </span>
                    </td>
                    <td>${pred.estimated_delay_hours.toFixed(1)}</td>
                `;
                tableBody.appendChild(tr);

                chartLabels.push(carrier);
                chartData.push(pred.risk_score);
            });

            // Render multi-carrier chart
            const ctx2 = document.getElementById('multiCarrierChart').getContext('2d');
            if (multiCarrierChart) {
                multiCarrierChart.destroy();
            }

            multiCarrierChart = new Chart(ctx2, {
                type: 'bar',
                data: {
                    labels: chartLabels,
                    datasets: [{
                        label: 'Delay Risk (%)',
                        data: chartData,
                        backgroundColor: 'rgba(37, 99, 235, 0.65)',
                        borderColor: 'rgba(37, 99, 235, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    scales: {
                        y: { beginAtZero: true, max: 100 }
                    },
                    plugins: {
                        legend: { display: false },
                        title: { display: true, text: 'Delay risk by carrier' }
                    }
                }
            });
        } catch (err) {
            console.error(err);
            alert("Failed to run multi-carrier simulation. Check if backend is running.");
        }
    });
}