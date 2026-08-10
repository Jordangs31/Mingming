let menu = document.querySelector('.header .menu');

document.querySelector('#menu-btn').onclick = () =>{
   menu.classList.toggle('active');
}

window.onscroll = () =>{
   menu.classList.remove('active');
}

document.querySelectorAll('input[type="number"]').forEach(inputNumber => {
   inputNumber.oninput = () =>{
      if(inputNumber.value.length > inputNumber.maxLength) inputNumber.value = inputNumber.value.slice(0, inputNumber.maxLength);
   };
});

document.querySelectorAll('.view-property .details .thumb .small-images img').forEach(images =>{
   images.onclick = () =>{
      src = images.getAttribute('src');
      document.querySelector('.view-property .details .thumb .big-image img').src = src;
   }
});

document.querySelectorAll('.faq .box-container .box h3').forEach(headings =>{
   headings.onclick = () =>{
      headings.parentElement.classList.toggle('active');
   }
});

// role_message.js
document.addEventListener('DOMContentLoaded', () => {
    const messages = document.querySelectorAll('.role-message');

    messages.forEach(msg => {
        const messageText = msg.dataset.message;
        const userType = msg.dataset.userType;

        if (messageText) {
            alert(messageText);  // simple pop-up
            // Optionally, you could customize with SweetAlert or a nicer modal
            console.log(`User type: ${userType}`);
        }
    });
});

const mainImage = document.getElementById("mainImage");
    const thumbnails = document.querySelectorAll(".thumb");

    let currentIndex = 0;

    // Convert NodeList to Array
    const images = Array.from(thumbnails);

    // CLICK THUMBNAIL
    images.forEach((img, index) => {
        img.addEventListener("click", function(){
            mainImage.src = this.src;
            currentIndex = index;
        });
    });

    // NEXT BUTTON
    document.getElementById("nextBtn").onclick = function(){
        currentIndex = (currentIndex + 1) % images.length;
        mainImage.src = images[currentIndex].src;
    };

    // PREV BUTTON
    document.getElementById("prevBtn").onclick = function(){
        currentIndex = (currentIndex - 1 + images.length) % images.length;
        mainImage.src = images[currentIndex].src;
    };

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

