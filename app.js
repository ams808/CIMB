document.addEventListener('DOMContentLoaded', function() {
    // Fetch and display total reserves
    fetch('/reserves')
        .then(response => response.json())
        .then(data => {
            document.getElementById('total-reserves').innerText = JSON.stringify(data);
        });

    // Fetch and display wallet balance and commodities
    // Placeholder, you'll need to implement wallet endpoints in your backend
    document.getElementById('wallet-balance').innerText = '0.00';
    document.getElementById('wallet-commodities').innerHTML = `
        <li>Gold: 0</li>
        <li>Silver: 0</li>
        <li>Platinum: 0</li>
    `;

    // Handle trade form submission
    document.getElementById('trade-form').addEventListener('submit', function(e) {
        e.preventDefault();
        const trader = document.getElementById('trader').value;
        const commodity = document.getElementById('commodity').value;
        const amount = document.getElementById('amount').value;

        fetch('/trade', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ trader, commodity, amount }),
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('trade-result').innerText = 'Trade successful!';
        })
        .catch(error => {
            document.getElementById('trade-result').innerText = 'Trade failed!';
        });
    });

    // Handle reserve form submission
    document.getElementById('reserve-form').addEventListener('submit', function(e) {
        e.preventDefault();
        const validator = document.getElementById('validator').value;
        const commodity = document.getElementById('reserve-commodity').value;
        const amount = document.getElementById('reserve-amount').value;

        fetch('/add_reserve', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ validator, commodity, amount }),
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('reserve-result').innerText = 'Reserve added successfully!';
        })
        .catch(error => {
            document.getElementById('reserve-result').innerText = 'Failed to add reserve!';
        });
    });
});
