(function() {
  'use strict';

    console.log('hello world');
  var recognition = new webkitSpeechRecognition();
  recognition.onresult = function(event) {
    console.log(event);
  }
  recognition.continuous = true;
  recognition.start();

})();
