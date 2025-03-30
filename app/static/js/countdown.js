// Configurar fecha final (ajusta a tu fecha de lanzamiento)
const launchDate = new Date("April 15, 2025 00:00:00").getTime();

// Actualizar contador cada segundo
const countdown = setInterval(function() {
  const now = new Date().getTime();
  const distance = launchDate - now;
  
  // Cálculos de tiempo
  const days = Math.floor(distance / (1000 * 60 * 60 * 24));
  const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
  const seconds = Math.floor((distance % (1000 * 60)) / 1000);
  
  // Mostrar resultado en elementos con id="days", "hours", etc.
  document.getElementById("days").innerText = days;
  document.getElementById("hours").innerText = hours;
  document.getElementById("minutes").innerText = minutes;
  document.getElementById("seconds").innerText = seconds;
  
  // Si la cuenta regresiva termina
  if (distance < 0) {
    clearInterval(countdown);
    document.getElementById("countdown").innerHTML = "¡Lanzamiento!";
    document.getElementById("launch-button").style.display = "block";
  }
}, 1000);