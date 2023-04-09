let slideIndex = 0;
const images = document.querySelectorAll(".slider-image");
const prevButton = document.querySelector(".prev-button");
const nextButton = document.querySelector(".next-button");

showSlide(slideIndex);

prevButton.addEventListener("click", () => {
  slideIndex--;
  if (slideIndex < 0) {
    slideIndex = images.length - 1;
  }
  showSlide(slideIndex);
});

nextButton.addEventListener("click", () => {
  slideIndex++;
  if (slideIndex > images.length - 1) {
    slideIndex = 0;
  }
  showSlide(slideIndex);
});

function showSlide(index) {
  for (let i = 0; i < images.length; i++) {
    images[i].classList.remove("active");
  }
  images[index].classList.add("active");
}
