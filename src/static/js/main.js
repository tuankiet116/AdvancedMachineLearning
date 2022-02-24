let video = document.getElementById("video");
let canvas = document.getElementById("myCanvas");
let ctx = canvas.getContext('2d');
let urlInput = document.getElementById("url");
let labels = document.getElementsByTagName('label');
let emailInput = document.getElementById("email");
let submitInput = document.getElementById("submit");
submitInput.onclick = login;
urlInput.value = "";
urlInput.setAttribute("accept", "image/png");
labels[1].hidden = "hidden";
emailInput.setAttribute("placeholder", "Email");
urlInput.setAttribute("placeholder", "URL");
urlInput.hidden = "hidden"
var localMediaStream = null;
var constraints = {
    video: {
        width: { max: 960 },
        height: { max: 720 }
    },
    audio: false
};

var selectDevice = document.getElementById('select-device');
checkDevices();
makeVideo();

async function checkDevices() {
    var devices = await navigator.mediaDevices.enumerateDevices()
    var options = '';
    devices.forEach(element => {
        if (element.deviceId != "") {
            options += `<option value="${element.deviceId}">${element.label}</option>`
        }
    });
    selectDevice.innerHTML = options;
}

selectDevice.addEventListener('change', function () {
    localMediaStream.getTracks()[0].stop();
    constraints.video.deviceId = this.value;
    makeVideo();
});

async function makeVideo() {
    navigator.mediaDevices.getUserMedia(constraints)
    .then(function (stream) {
        video.srcObject = stream;
        localMediaStream = stream;
    })
    .catch(function (error) {
        console.log(error);
    });
}

function login() {
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    var dataURL = canvas.toDataURL('image/png');
    document.getElementById("url").value = dataURL;
}