const inputs = document.querySelectorAll(".input-field");
const toggle_btn = document.querySelectorAll(".toggle");
const main = document.querySelector("main");
const bullets = document.querySelectorAll(".bullets span");
const images = document.querySelectorAll(".image");

inputs.forEach((inp) => {
  inp.addEventListener("focus", () => {
    inp.classList.add("active");
  });
  inp.addEventListener("blur", () => {
    if (inp.value != "") return;
    inp.classList.remove("active");
  });
});

toggle_btn.forEach((btn) => {
  btn.addEventListener("click", () => {
    main.classList.toggle("sign-up-mode");
  });
});

function moveSlider() {
  let index = this.dataset.value;

  let currentImage = document.querySelector(`.img-${index}`);
  images.forEach((img) => img.classList.remove("show"));
  currentImage.classList.add("show");

  const textSlider = document.querySelector(".text-group");
  textSlider.style.transform = `translateY(${-(index - 1) * 2.2}rem)`;

  bullets.forEach((bull) => bull.classList.remove("active"));
  this.classList.add("active");
}

bullets.forEach((bullet) => {
  bullet.addEventListener("click", moveSlider);
});


// Assuming you're using Fetch API for making asynchronous requests

document.querySelector('.sign-in-form').addEventListener('submit', async function (event) {
 

  const form = event.target;
  const formData = new FormData(form);

  try {
      const response = await fetch('/login', {
          method: 'POST',
          body: formData,
      });

      const result = await response.json();

      if (result.test) {
          // Redirect to the logged-in page
          window.location.href = result.redirect;
      } else {
          // Display an error message or handle it as needed
          console.log("Login failed. Incorrect username or password.");
      }
  } catch (error) {
      console.error("An error occurred:", error);
  }
});
