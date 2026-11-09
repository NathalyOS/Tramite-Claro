(function () {
  const cuerpo = document.body;
  const boton = document.querySelector("#btn-lectura-clara");
  const minimo = 16;
  const maximo = 28;
  const paso = 2;

  function aplicar(activa) {
    cuerpo.classList.toggle("lectura-clara", activa);
    if (boton) {
      boton.setAttribute("aria-pressed", activa ? "true" : "false");
    }
  }

  function tamanoGuardado() {
    const guardado = Number(localStorage.getItem("tamano-letra"));
    if (guardado >= minimo && guardado <= maximo) {
      return guardado;
    }
    return 0;
  }

  function aplicarTamano(px) {
    const tamano = Math.min(maximo, Math.max(minimo, px));
    localStorage.setItem("tamano-letra", String(tamano));
    document.documentElement.style.setProperty("--tamano-letra", tamano + "px");
    if (botonMenos) {
      botonMenos.disabled = tamano <= minimo;
    }
    if (botonMas) {
      botonMas.disabled = tamano >= maximo;
    }
  }

  function tamanoActual() {
    const guardado = tamanoGuardado();
    if (guardado) {
      return guardado;
    }
    return cuerpo.classList.contains("lectura-clara") ? 18 : 16;
  }

  aplicar(localStorage.getItem("lectura-clara") === "1");
  const yaElegido = tamanoGuardado();
  if (yaElegido) {
    document.documentElement.style.setProperty("--tamano-letra", yaElegido + "px");
  }

  if (!boton) {
    return;
  }

  const botonMenos = document.createElement("button");
  botonMenos.type = "button";
  botonMenos.className = "btn btn-outline-light ms-lg-2 my-2 my-lg-0";
  botonMenos.textContent = "A−";
  botonMenos.setAttribute("aria-label", "Letra más chica");
  botonMenos.disabled = tamanoActual() <= minimo;

  const botonMas = document.createElement("button");
  botonMas.type = "button";
  botonMas.className = "btn btn-outline-light ms-1 my-2 my-lg-0";
  botonMas.textContent = "A+";
  botonMas.setAttribute("aria-label", "Letra más grande");
  botonMas.disabled = tamanoActual() >= maximo;

  boton.insertAdjacentElement("afterend", botonMas);
  boton.insertAdjacentElement("afterend", botonMenos);

  boton.addEventListener("click", () => {
    const activa = !cuerpo.classList.contains("lectura-clara");
    localStorage.setItem("lectura-clara", activa ? "1" : "0");
    aplicar(activa);
  });

  botonMenos.addEventListener("click", () => {
    aplicarTamano(tamanoActual() - paso);
  });

  botonMas.addEventListener("click", () => {
    aplicarTamano(tamanoActual() + paso);
  });
})();
