document.addEventListener("click", function (e) {
  if (e.target.classList.contains("mapa")) {
    console.log("soy el mapa");
    const src = e.target.getAttribute("id");
    document.querySelector(".modal-img").src = src;
    const myModal = new bootstrap.Modal(
      document.getElementById("gallery-modal")
    );
    myModal.show();
  }
});