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
  document.getElementById("scrollable-chats-tc").style.display = "none";
  document.getElementById("scrollable-chats-pm").style.display = "block";
}

function toTc() {
  document.getElementById("tc").style.backgroundColor = "white";
  document.getElementById("pm").style.backgroundColor = "#BFBFBF";
  document.getElementById("scrollable-chats-pm").style.display = "none";
  document.getElementById("scrollable-chats-tc").style.display = "block";
}
