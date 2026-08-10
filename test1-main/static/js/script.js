// =========================
// MENU TOGGLE (SAFE)
// =========================
const menu = document.querySelector('.header .menu');
const menuBtn = document.querySelector('#menu-btn');

if(menu && menuBtn){
   menuBtn.onclick = () => {
      menu.classList.toggle('active');
   };

   window.addEventListener('scroll', () => {
      menu.classList.remove('active');
   });
}


// =========================
// NUMBER INPUT LIMIT FIX
// =========================
document.querySelectorAll('input[type="number"]').forEach(input => {
   input.addEventListener("input", () => {
      if(input.max){
         input.value = Math.min(input.value, input.max);
      }
   });
});


// =========================
// PROPERTY IMAGE SYSTEM
// (CLICK + SLIDER + ZOOM)
// =========================
const mainImage = document.getElementById("mainImage");
const thumbnails = document.querySelectorAll(".gallery img");
const nextBtn = document.getElementById("nextBtn");
const prevBtn = document.getElementById("prevBtn");

if(mainImage && thumbnails.length > 0){

   let currentIndex = 0;
   const images = Array.from(thumbnails);

   // CLICK THUMBNAIL
   images.forEach((img, index) => {
      img.addEventListener("click", function(){
         mainImage.src = this.src;
         currentIndex = index;
      });
   });

   // NEXT BUTTON
   if(nextBtn){
      nextBtn.addEventListener("click", () => {
         currentIndex = (currentIndex + 1) % images.length;
         mainImage.src = images[currentIndex].src;
      });
   }

   // PREVIOUS BUTTON
   if(prevBtn){
      prevBtn.addEventListener("click", () => {
         currentIndex = (currentIndex - 1 + images.length) % images.length;
         mainImage.src = images[currentIndex].src;
      });
   }

   // ZOOM EFFECT
   mainImage.addEventListener("mousemove", function(e){
      const rect = this.getBoundingClientRect();
      const x = ((e.clientX - rect.left) / rect.width) * 100;
      const y = ((e.clientY - rect.top) / rect.height) * 100;

      this.style.transformOrigin = x + "% " + y + "%";
      this.style.transform = "scale(2)";
   });

   mainImage.addEventListener("mouseleave", function(){
      this.style.transform = "scale(1)";
   });
}


// =========================
// FAQ TOGGLE
// =========================
document.querySelectorAll('.faq .box-container .box h3').forEach(head => {
   head.addEventListener("click", () => {
      head.parentElement.classList.toggle('active');
   });
});


// =========================
// ROLE MESSAGE ALERT
// =========================
document.addEventListener('DOMContentLoaded', () => {
   const messages = document.querySelectorAll('.role-message');

   messages.forEach(msg => {
      const messageText = msg.dataset.message;
      const userType = msg.dataset.userType;

      if(messageText){
         alert(messageText);
         console.log(`User type: ${userType}`);
      }
   });
});