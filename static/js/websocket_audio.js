var play_check = false;
var first_play = true;
var begin = Date.now();  // 当前时间

const buffer = [];   // 缓存
play_button = document.getElementById('playButton');
play_button.addEventListener('click', function() {
    if (play_check == true){
        play_check = false;
        play_button.innerHTML = '开始播放';
    }
    else{
    socket.send('Get_AudioData');
    play_button.innerHTML = '暂停播放';
     play_check = true;
    }
});

function sleep(ms) {  // 睡眠
  return new Promise(resolve => setTimeout(resolve, ms));
}

//var audioElement = document.getElementById('audioPlayer');
var audioElement = new Audio();
//audioElement.addEventListener('timeupdate', function() {
//    if (audioElement.currentTime >= 1.2) { // 当播放到 1.3 秒时
//      audioElement.pause(); // 暂停音频
//      audioPlayerPlay();
//    }
//});
audioElement.addEventListener('ended', () => {   // 播放完成的回调函数
   console.log(buffer.length);
   if (buffer.length > 0){
       const data = buffer.shift();
       var audioURL = URL.createObjectURL(data);
       audioElement.src = audioURL;
       console.log('播放时间为' + (Date.now() - begin));
       begin = Date.now();
       audioElement.play();
       socket.send('Get_AudioData');
       return;
   }
   first_play = true;
});

const socket = new WebSocket('ws://10.22.218.145:5001');
    socket.onopen = function(event) {
        console.log('WebSocket 连接已建立');

    };

    socket.onmessage = function(event) {
        var audioURL = URL.createObjectURL(event.data);
        if (play_check == true)
        {
            // 播放音频
            if (first_play){
                audioElement.src = audioURL;
                audioElement.play();
                first_play = false;
                socket.send('Get_AudioData');
            }
            else{
                buffer.push(event.data);
            }
        }
    };

    socket.onclose = function(event) {
        if (event.wasClean) {
            console.log('WebSocket 连接已关闭');
        } else {
            console.error('WebSocket 连接断开');
        }
    };

    socket.onerror = function(error) {
        console.error('WebSocket 错误: ' + error.message);
    };

function audioPlayerPlay(){
    if (buffer.length > 0){
       const data = buffer.shift();
       var audioURL = URL.createObjectURL(data);
       audioElement.src = audioURL;
       console.log('播放时间为' + (Date.now() - begin));
       begin = Date.now();
       audioElement.play();
       return;
   }
   first_play = true;
}