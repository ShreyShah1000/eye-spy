const video = document.getElementById('video')
const canvas = document.getElementById('canvas')
const snap = document.getElementById('snap')
const ctx = canvas.getContext('2d')
const voiceInput = document.getElementById('voice-input')
const micBtn = document.getElementById('mic-btn')

var object;
var riddle;

var tries;

let recognition;
let isRecording = false;

$("#game").hide();

$("#answer-layout").hide();
$("#answer-panel").hide();

function init(){
    // get webcam stream
    navigator.mediaDevices.getUserMedia({ video: true })
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

    // This is now a proper JavaScript object, which is how JSON is represented in JS.
    const response = {
        "id": "gen-1762031287-AwmPQC5KW1AelV5koxQQ",
        "provider": "Alibaba",
        "model": "qwen/qwen3-vl-8b-instruct",
        "object": "chat.completion",
        "created": 1762031287,
        "choices": [
            {
                "logprobs": null,
                "finish_reason": "stop",
                "native_finish_reason": "stop",
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "{\"object\":\"lanyard\",\"riddle\":\"I hang around necks, with colors that gleam, a badge holder I am, not a dream.\",\"reason\":\"The lanyard is distinct, colorful, and clearly visible against the gray shirt, making it a perfect I Spy target.\"}",
                    "refusal": null,
                    "reasoning": null
                }
            }
        ],
        "system_fingerprint": null,
        "usage": {"prompt_tokens": 1670, "completion_tokens": 68, "total_tokens": 1738}
    };

    // fetch('http://127.0.0.1:5500/processImage', {
    //     method: 'POST',
    //     headers: { 'Content-Type': 'application/json' },
    //     body: JSON.stringify({ image: dataURL })
    // })
    // .then(res => res.text())
    // .then(text => {
    //     var response = text
    // })
    // .catch(console.error)

    if(response){
        // The 'content' is a JSON string, so it needs to be parsed separately.
        const gameData = JSON.parse(response.choices[0].message.content);
        
        object = gameData.object; // "lanyard"
        riddle = gameData.riddle; // "I hang around necks..."

        tries = 3;

        $("#camera").hide()
        $("#game").show()

        $("#riddle").text(riddle)
        $("#riddle").addClass('o fast')

        setTimeout(() => {
            $("#riddle").removeClass('o')
        }, 500)
    }
});

function inputAnswer(elem){
    if(Math.abs($(elem).val().localeCompare(object)) < 10){
        //correct
        $("#answer").text(object)

        toggleFloating('answer-layout', 'answer-video')        
    }else{
        // incorrect
        $("#tries").val('')

        tries--
    }
}