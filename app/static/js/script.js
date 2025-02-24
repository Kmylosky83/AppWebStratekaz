function setup() {
    createCanvas(400, 400); // Crea un lienzo de 400x400 píxeles
  }
  
  function draw() {
    background(220); // Establece el color de fondo
  
    // Dibuja el laberinto (puedes personalizar el diseño del laberinto aquí)
    line(50, 50, 350, 50);
    line(350, 50, 350, 350);
    line(350, 350, 50, 350);
    line(50, 350, 50, 50);
  }