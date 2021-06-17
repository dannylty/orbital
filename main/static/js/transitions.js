document.getElementById("profile").addEventListener("mouseover", mouseOver);
document.getElementById("profile").addEventListener("mouseout", mouseOut);

function mouseOver() {
  document.getElementById("profilemenu").style.visibility = "visible";
}

function mouseOut() {
  document.getElementById("profilemenu").style.visibility = "hidden";
}
