// ============================================================
// CampusCare — vanilla JS (no frameworks, no external APIs)
// Small UX touches only. All real logic happens on the server.
// ============================================================

document.addEventListener("DOMContentLoaded", function () {

  // Auto-dismiss flash messages after 5 seconds
  document.querySelectorAll(".flash").forEach(function (el) {
    setTimeout(function () {
      el.style.transition = "opacity .4s ease";
      el.style.opacity = "0";
      setTimeout(function () { el.remove(); }, 400);
    }, 5000);
  });

  // Client-side password match check on the register form
  var registerForm = document.querySelector('form[action*="register"]');
  if (registerForm) {
    registerForm.addEventListener("submit", function (e) {
      var pw = document.getElementById("password");
      var cpw = document.getElementById("confirm_password");
      if (pw && cpw && pw.value !== cpw.value) {
        e.preventDefault();
        alert("Passwords match nahi kar rahe, dobara check karo!");
        cpw.focus();
      }
    });
  }

  // Simple character counter on the complaint description box
  var desc = document.getElementById("description");
  if (desc) {
    var counter = document.createElement("div");
    counter.style.fontSize = "11px";
    counter.style.color = "#a9a08d";
    counter.style.marginTop = "4px";
    counter.textContent = desc.value.length + " characters";
    desc.insertAdjacentElement("afterend", counter);
    desc.addEventListener("input", function () {
      counter.textContent = desc.value.length + " characters";
    });
  }

});
