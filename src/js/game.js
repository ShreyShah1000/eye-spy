import {Conversation} from 'https://esm.sh/@elevenlabs/client';

const video = document.getElementById('video')
const canvas = document.getElementById('canvas')
const snap = document.getElementById('snap')
const ctx = canvas.getContext('2d')
const voiceInput = document.getElementById('voice-input')
const micBtn = document.getElementById('mic-btn')

var object
var riddle

var tries
var points

var difficulty = 5

let recognition
let isRecording = false

var voiceMode = false

var conversation

$("#game").hide()

hideAll()

$("#video-layout").hide()
$("#video-panel").hide()

function init(){
    tries = 3
    points = 0
    difficulty = 5

    updateCounts()

    // get webcam stream
    navigator.mediaDevices.getUserMedia({ video: true, audio: true })
        .then(stream => {
            video.srcObject = stream
            $(".loading").hide()
        })
        .catch(err => console.error("Camera access denied:", err))

        // Initialize speech recognition
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'en-US';

            recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                voiceInput.value = transcript;
            };

            recognition.onend = () => {
                isRecording = false;
                micBtn.innerHTML = '<i class="material-symbols-rounded">mic</i>';
            };

            recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                isRecording = false;
                micBtn.innerHTML = '<i class="material-symbols-rounded">mic</i>';
            };
        } else {
            console.warn('Speech recognition not supported in this browser.');
            micBtn.disabled = true;
        }
    }

    // Voice input toggle
    micBtn.addEventListener('click', () => {
    if (!recognition) return;

    if (isRecording) {
        recognition.stop();
    } else {
        recognition.start();
        isRecording = true;
        micBtn.innerHTML = '<i class="material-symbols-rounded">stop_circle</i>';
    }
});

// capture a frame and send to backend
snap.addEventListener('click', () => {
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
    const dataURL = canvas.toDataURL('image/jpeg') // base64 JPEG

    var response;

    fetch('https://eye-spy-backend.onrender.com/processImage', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image: dataURL })
    })
    .then(res => {
        return res.text(); // Get the response body as text
    })
    .then(responseText => {
        if (responseText) {
            if(voiceMode)
                startAgent()
            else{
                // The 'content' is a JSON string, so it needs to be parsed separately.
                const gameData = JSON.parse(responseText)
                console.log(gameData)
                
                object = gameData.object.replace(/_/g, " ")

                riddle = gameData.riddle

                $("#fun-fact").text(gameData.fact)

                $("#death-answer").text(object)

                tries = 3

                $("#camera").hide()
                $("#game").show()

                $("#riddle").text(riddle)
                $("#riddle").addClass('o fast')


                setTimeout(() => {
                    $("#riddle").removeClass('o fast')
                }, 500)
            }
        }
    })
    .catch(console.error)
});

function inputAnswer(){
    if($("#voice-input").val() == object){
        //correct
        $("#answer").text(object)

        points += tries * difficulty

        updateCounts()

        // Only submit score if not in voice mode (agent will handle it)
        if (!voiceMode) {
            submitScore()
        }

        endAgent()

        toggleFloating('answer-layout', 'answer-panel')        
    }else{
        if(tries == 1){
            toggleFloating('wrong-layout', 'wrong-panel')
            toggleFloating('dead-layout', 'dead-panel')

            // Only submit final score when game ends if not in voice mode
            if (!voiceMode) {
                submitScore()
            }

            return
        }

        // incorrect
        tries--
        $("#tries").text(tries)

        updateCounts()

        if(localStorage.getItem('points') == null){
            localStorage.setItem('points', points)
        }else{
            localStorage.setItem('points', localStorage.getItem('points') + points)
        }

        toggleFloating('wrong-layout', 'wrong-panel')
    }
}

function submitScore() {
    const username = localStorage.getItem('eyespy_username');
    if (!username) {
        console.log('No username found, skipping score submission');
        return;
    }

    fetch('https://eye-spy-backend.onrender.com/score/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            username: username,
            score: points
        })
    })
    .then(res => res.json())
    .then(data => {
        console.log('Score submitted:', data);
    })
    .catch(err => {
        console.error('Error submitting score:', err);
    });
}

function updateCounts(){
    $("#tries-count").text(tries)
    $("#points-count").text(points)
}

function tryAgain(){
    toggleFloating('wrong-layout', 'wrong-panel')
}

function nextRound(){
    tries = 3

    hideAll()

    $("#game").hide()
    $("#camera").show()
}

function hideAll(){
    $("#answer-layout").hide()
    $("#answer-panel").hide()
    $("#wrong-layout").hide()
    $("#wrong-panel").hide()
    $("#dead-layout").hide()
    $("#dead-panel").hide()
}

function startAgent(){
    if(conversation){
        return
    }

    voiceMode = true
    conversation = Conversation.startSession({
        agentId: "agent_7801k90mdswcfpcsp95wskaaq3ry",
        connectionType: "webrtc",
    })
}

async function endAgent(){
    voiceMode = false
    await conversation.endSession()
}

function toggleVoice(){
    toggle('voice-mode')

    voiceMode = !voiceMode
    if(voiceMode){
        endAgent()
        $(".stats").show()
    }else{
        startAgent()
        $(".stats").hide()
    }
}

window.init = init
window.inputAnswer = inputAnswer
window.tryAgain = tryAgain
window.nextRound = nextRound
window.startAgent = startAgent
window.endAgent = endAgent
window.toggleVoice = toggleVoice
window.submitScore = submitScore