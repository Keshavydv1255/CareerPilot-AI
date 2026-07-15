// Animate statistics when page loads
window.addEventListener("load", () => {

    const stats = document.querySelectorAll(".stat-card h2");

    stats.forEach(stat => {

        const finalValue = stat.innerText;

        // Skip text values like "AI"
        if (isNaN(finalValue)) return;

        let current = 0;

        const target = parseInt(finalValue);

        const timer = setInterval(() => {

            current++;

            stat.innerText = current;

            if (current >= target) {

                clearInterval(timer);

            }

        }, 40);

    });

});

// Dark Mode Toggle
function toggleTheme(){

    document.body.classList.toggle("dark");

    localStorage.setItem(
        "careerTheme",
        document.body.classList.contains("dark")
            ? "dark"
            : "light"
    );

}

// Restore saved theme
window.onload = function(){

    if(localStorage.getItem("careerTheme")==="dark"){

        document.body.classList.add("dark");

    }

}