(function(){
    var app = angular.module('proctor.date', []);
    app.service('DateTimeService', function($rootScope, $interval){
        var ticker = null;
        var self = this;
        var default_lng = 'ru';

        String.prototype.toHHMMSS = function () {
            var sec_num = parseInt(this, 10); // don't forget the second param
            var hours   = Math.floor(sec_num / 3600);
            var minutes = Math.floor((sec_num - (hours * 3600)) / 60);
            var seconds = sec_num - (hours * 3600) - (minutes * 60);

            if (hours   < 10) {hours   = "0"+hours;}
            if (minutes < 10) {minutes = "0"+minutes;}
            if (seconds < 10) {seconds = "0"+seconds;}
            var time    = hours+':'+minutes+':'+seconds;
            return time;
        }

        this.value = null;

        var date_options = {
            year: 'numeric', month: 'long',  day: 'numeric',
            weekday: 'long', hour: 'numeric', minute: 'numeric', second: 'numeric'
        };

        var localDate = function(loc){
            var d = new Date();
            return d.toLocaleString(loc, date_options);
        };

        this.start_timer = function(){
            ticker = $interval(function(){
                var l = window.localStorage['NG_TRANSLATE_LANG_KEY'];
                self.value = localDate(l !== undefined?l:default_lng);
            }, 1000);
        };

        this.stop_timer = function(){
            $interval.cancel(ticker);
            ticker = null;
        };

        this.get_now_diff_from_string = function(date_str){
            var diff = parseInt((Date.now() - Date.parse(date_str))/1000);
            return ("" + diff).toHHMMSS();
        };

        this.get_now_date = function(){
            var today = new Date();
            var dd = today.getDate();
            var mm = today.getMonth()+1; //January is 0!
            var yyyy = today.getFullYear();

            if(dd<10) {
                dd='0'+dd
            }

            if(mm<10) {
                mm='0'+mm
            }

            return dd+'.'+mm+'.'+yyyy;
        };

        $rootScope.$watch(function(){
            if (window.localStorage['NG_TRANSLATE_LANG_KEY'] !== undefined){
                return window.localStorage['NG_TRANSLATE_LANG_KEY'];
            }
            else
                return default_lng;
        }, function(){
            if (ticker) {
                self.stop_timer();
                self.start_timer();
            }
        }, true);
    });
})();