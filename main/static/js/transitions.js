document.getElementById("profile").addEventListener("mouseover", mouseOver);
document.getElementById("profile").addEventListener("mouseout", mouseOut);

function mouseOver() {
  document.getElementById("profilemenu").style.visibility = "visible";
}

function mouseOut() {
  document.getElementById("profilemenu").style.visibility = "hidden";
}


function toPm() {
  document.getElementById("tc").style.backgroundColor = "#BFBFBF";
  document.getElementById("pm").style.backgroundColor = "white";
  document.getElementsByClassName("scrollable-chats-tc")[0].style.visibility = "hidden";
  document.getElementsByClassName("scrollable-chats-pm")[0].style.visibility = "visible";
}

function toTc() {
  document.getElementById("tc").style.backgroundColor = "white";
  document.getElementById("pm").style.backgroundColor = "#BFBFBF";
  document.getElementsByClassName("scrollable-chats-tc")[0].style.visibility = "visible";
  document.getElementsByClassName("scrollable-chats-pm")[0].style.visibility = "hidden";
}
