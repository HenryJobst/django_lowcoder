const spinnerBox = document.getElementById('spinner-box');
const theSpinnerButton = document.querySelector(".spinner-btn");
if (spinnerBox != null && theSpinnerButton != null) {
 theSpinnerButton.addEventListener("click", () => {
        spinnerBox.classList.remove("not-visible");
    });
}
