'use strict';

/****************************************************************************
* Initial setup
****************************************************************************/

// var configuration = {
//   'iceServers': [{
//     'urls': 'stun:stun.l.google.com:19302'
//   }]
// };


var configuration = null;

// var roomURL = document.getElementById('url');
//html 에 있는 객체에 대한 참조를 가져온다. 
var video = document.querySelector('video');      // 비디오 
var photo = document.getElementById('photo');     // 사진 
var photoContext = photo.getContext('2d');   


var d_id = document.getElementById('d_id');       // 드론아이디
var snapBtn = document.getElementById('snap');    // 스냅버튼
var startBtn = document.getElementById('start');  // 시작버튼
var stopBtn = document.getElementById('stop');    // 정지버튼
var msg = document.getElementById('status_msg');  // 데이터 저장 상태 확인 메세지


var photoContextW;
var photoContextH;

// 버튼에 이벤트 핸들러를 붙인다.  
//d_id.addEventListener('blur',id_input)
snapBtn.addEventListener('click',  snapPhoto)
startBtn.addEventListener('click', start); // 동영상 캡처 및 서버 저장 시작
stopBtn.addEventListener('click', stop); // 캡처 정지 서버 저장 정지
 
// Disable send buttons by default.

startBtn.disabled = false
stopBtn.disabled = true

function snapPhoto(){
  photoContext.drawImage(video, 0, 0, photo.width, photo.height);
}



/****************************************************************************
* User media (webcam)
****************************************************************************/
function grabWebCamVideo() {
  console.log('Getting user media (video) ...');
  //비동기 모드, 장치에 대한 접근이 허용되면  then 이하가 실행된다.
  //Initializes media stream. 
  navigator.mediaDevices.getUserMedia({
    audio: false,
    video: { width: 480, height: 360 },  //비디오만 

  })
  .then(gotStream)  //스트립을 처리할 함수의 주소를 전달한다
  .catch(function(e) {
    alert('getUserMedia() error: ' + e.name);
  });
}

function gotStream(stream) {
  //여기서 스트림을 처리한다 
  console.log('getUserMedia video stream URL:', stream);
  window.stream = stream; // stream available to console
  video.srcObject = stream;
  //비디오가 준비가 되면 이
  video.onloadedmetadata = function() {
    photo.width = photoContextW = video.videoWidth;
    photo.height = photoContextH = video.videoHeight;
    console.log('gotStream with width and height:', photoContextW, photoContextH);
  };
  show(snapBtn);
}

/*
function get_location()
{
  fetch('https://ipapi.co/json/')
  .then(function(response) {
    return response.json();
  })
  .then(function(data) {
    //console.log(data);
    ip_address = data['ip']
    latitude = data['latitude']
    longitude = data['longitude']
    console.log(ip_address,latitude,longitude)
  });

}
*/
function getGPS(){ //navigator 바를 이용하여 ip주소로 부터  x,y 좌표 위치를 얻어오는 함수.
                   // 좌표정보는 카카오 페이지를 위한 Ajax함수로 넘김
  navigator.geolocation.getCurrentPosition(function(pos) {
    var latitude = pos.coords.latitude;
    var longitude = pos.coords.longitude; 
    console.log(latitude, longitude );
    kakaoApi(longitude, latitude);
  });
}

/****************************************************************************
*시작 및 정지 기능 제어함수
****************************************************************************/


var timerId = null; // setInterval 함수의 Id저장을 위한 변수


function start(){
  if (document.getElementById('d_id').value=='') // ID 항목이 공백일경우
  {
    alert('드론아이디를 채우세요');               // 경고메세지 출력
    document.getElementById('d_id').focus();    // 텍스트 페이지로 포커싱하여 텍스트 입력이 가능하도록 
    return false;                               //  함수 종료
  }
  status_msg.innerText = '데이터 업로딩...'      // 아이디가 있을경우 데이터 업로딩 메세지 출력
  timerId = setInterval(getGPS,3000);           // 3초마다 x,y좌표 얻어온 후 이미지를 저장

  //  getGPS  ->      kakaoApi        ->     ajax_server
  //  좌표얻음 -> 좌표로부터 주소 얻음  ->  얻은 데이터들을 save함수에 전송

  startBtn.disabled = true;                     // 시작버튼을 비활성화 하여 함수의 중복이 안되게 설정
  stopBtn.disabled = false;                     // stop 버튼 활성화
}

function stop(){
  if(timerId != null) {             // 만약 timeId값이 있을경우
    clearInterval(timerId);         // 인터벌 함수 정지
    startBtn.disabled = false;
    stopBtn.disabled =true
    status_msg.innerText = '데이터 업로드가 중지되었습니다.'
  }

}

// 지정된 GPS 좌표로부터 주소를 얻어옴
function kakaoApi(longitude,latitude) {

    //console.log(d_id)
    $.ajax({
      type: "POST",
      headers:{"Authorization":'KakaoAK 876e9dd3cee1b67c2f15c6a58cd44f9c'},
      url: "https://dapi.kakao.com/v2/local/geo/coord2address.json?x="+longitude+"&y="+latitude+"&input_coord=WGS84",  //받아서 저장하자 
    }).done(function(msg){ 
        var address = msg['documents'][0]['address']
        //console.log(address['address_name'])
        ajax_send(longitude,latitude,address['address_name'])  
      }
    )
 
}

//완성된 정보를 서버로 보낸다.
function ajax_send(x, y, address)
{
  photoContext.drawImage(video, 0, 0, photo.width, photo.height);
  var dataURL = photo.toDataURL();
  $.ajax({  
    type: "POST",
    url:'/save',      //board의 save에 해당하는 함수를 실행시킴으로 써 PC에 사진데이터를 저장
    data: {'d_id':d_id.value, 'img': dataURL, 'x':x, 'y':y,'add':address}      
  }).done(function(msg){ 
    console.log(msg); 
  });
}





function show() {
  Array.prototype.forEach.call(arguments, function(elem) {
    elem.style.display = null;
  });
}

function hide() {
  Array.prototype.forEach.call(arguments, function(elem) {
    elem.style.display = 'none';
  });
}

function logError(err) {
  if (!err) return;
  if (typeof err === 'string') {
    console.warn(err);
  } else {
    console.warn(err.toString(), err);
  }
}


  