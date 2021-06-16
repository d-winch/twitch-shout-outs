// Get query string
const queryString = window.location.search;
console.log(queryString);

// Get params
const urlParams = new URLSearchParams(queryString);
const broadcastUsername = urlParams.get("username");
const max_duration = urlParams.get("max_duration");
let muted = urlParams.get("muted") === "true";
console.log(broadcastUsername, max_duration, muted);

// Get elements
const shoutText = document.getElementById("shoutText");
const userText = document.getElementById("usernameText");
const video = document.getElementById("video");

let isActive = true;
let isClipPlaying = false;
let shoutOuts = [];

ComfyJS.Init(broadcastUsername);

ComfyJS.onCommand = (user, command, message, flags, extra) => {

  // Return if the command was not by the broadcaster or a mod
  if (!flags.broadcaster && !flags.mod) {
    return
  }

  if (command === "so") {
    if (isActive) {
      console.log("!so by " + user);
      shoutOut(message);
    } else {
      console.log("!so by " + user + " but shoutouts are disabled");
    }
    return;
  }

  if (command === "soreload") {
    location.reload();
    console.log("!soreload by " + user); // Log after reload for where persistant logs disabled
    return;
  }

  if (command === "soon") {
    console.log("!soon by " + user);
    isActive = true;
    return;
  }

  if (command === "sooff") {
    console.log("!sooff by " + user);
    isActive = false;
    return;
  }

  if (command === "somute") {
    console.log("!somute by " + user);
    muted = true;
    video.muted = true;
    return;
  }

  if (command === "sounmute") {
    console.log("!sounmute by " + user);
    muted = false;
    video.muted = false;
    return;
  }

  if (command === "sostop") {
    // BROKEN DUE TO VIDEO PLAY PROMISE
    console.log("!sostop by " + user);
    shoutOuts = shoutOuts.slice(1);
    resetShout();
    return;
  }
};

ComfyJS.onRaid = (user, viewers, extra) => {
  // TO-DO
  // Auto shout out raiders if enabled
};

ComfyJS.onError = (error) => {
  // TO-DO
  // Set variables which may have been changed (mute, isActive, etc)
  location.reload();
  console.log("Error", error);
};

function status(response) {
  if (response.status >= 200 && response.status < 300) {
    return Promise.resolve(response);
  } else {
    return Promise.reject(new Error(response.statusText));
  }
}

function json(response) {
  return response.json();
}

function shoutOut(message) {
  console.log("shoutOut function called with message " + message);
  let username = message.split(" ")[0].replace("@", "");
  console.log("User: " + username);

  fetch(window.location.origin + "/soclip/" + username)
    .then(status)
    .then(json)
    .then(function (data) {
      console.log("Success:", data);
      shoutOuts.push(data);
      console.log(shoutOuts);
    })
    .catch(function (error) {
      console.log("Request failed", error);
    });
}

function playVideo(shoutOutData) {
  console.log("playVideo called");
  username = shoutOutData["username"];
  url = shoutOutData["url"];

  userText.textContent = username.toUpperCase();
  video.setAttribute("src", url);

  video.muted = muted;
  video.play();
  shoutText.style.visibility = "visible";
  video.style.visibility = "visible";
}

function resetShout() {
  console.log("resetShout called");
  isClipPlaying = false;
  shoutText.style.visibility = "hidden";
  video.style.visibility = "hidden";
  video.setAttribute("src", "");
  video.muted = true;
  video.currentTime = 0;
}

video.onplaying = function () {
  console.log("video.onplaying called");
  isClipPlaying = true;
};

video.onended = function () {
  console.log("video.onended called");
  resetShout();
};

setInterval(function () {
  //isClipPlaying =
  //  video.currentTime > 0 &&
  //  !video.paused &&
  //  !video.ended &&
  //  video.readyState > video.HAVE_CURRENT_DATA;
  if (shoutOuts.length > 0) {
    if (!isClipPlaying) {
      console.log("We have a shout and a clip is not playing");
      isClipPlaying = true;
      playVideo(shoutOuts[0]);
      shoutOuts = shoutOuts.slice(1);
      return;
    }
  }
  if (video.currentTime >= max_duration) {
    console.log("Max duration exceeded, ending early");
    resetShout();
  }
}, 1000);