document.addEventListener('DOMContentLoaded', function () {
    // Order Status Chart
    const statusCounts = JSON.parse(document.getElementById('status-counts-data').textContent);

    // Extract labels and data from status_counts
    let labels = [];
    let data = [];
    let backgroundColors = [];

    const colorMap = {
        'new': '#6c757d',       // secondary
        'design': '#0d6efd',    // primary
        'preparation': '#0dcaf0', // info
        'delivery': '#ffc107',  // warning
        'completed': '#198754', // success
        'cancelled': '#dc3545'  // danger
    };

    statusCounts.forEach(function (item) {
        labels.push(item.status.charAt(0).toUpperCase() + item.status.slice(1));
        data.push(item.count);
        backgroundColors.push(colorMap[item.status] || '#6c757d');
    });

    const ctx = document.getElementById('orderStatusChart').getContext('2d');
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: backgroundColors,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom',
                }
            }
        }
    });
});
