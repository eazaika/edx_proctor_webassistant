'use strict';

(function(){
    var module = angular.module('tokenAuth', []);
    module.service('Auth', ['$cookies', '$q', '$http', 'permissions', function($cookies, $q, $http, permissions){
        var token = '';
        var username1 = $cookies.get('authenticated_user');
        var username = username1.replace(/['"«»]/g, '');
        var restrictions = null;
        var self = this;

        this.authenticate = function(){
            var c = $cookies.get('authenticated_token');
            if (c !== undefined && c){
                token = c;
                //$cookies.put('authenticated_token', undefined);
                return true;
            }
            return false;
        };

        this.get_token = function(){
            if (self.authenticate())
                return token;
            else
                return '';
        };

        this.get_proctor = function(){
            return username;
        };

        this.is_role = function(rolename) {
            var deferred = $q.defer();
            if (self.authenticate()) {
                permissions.get().then(function(data){
                    restrictions = data.data;
                    deferred.resolve(restrictions.role == rolename);
                }, function(){
                    deferred.resolve(false);
                });
            }
            else{
                deferred.resolve(false);
            }
            return deferred.promise;
        };

        this.is_proctor = function(){
            return this.is_role('proctor');
        };

        this.is_instructor = function(){
            return this.is_role('instructor');
        };
    }]);

    module.factory('permissions', function($rootScope, $http){
        var get = function(){
            return $http({
                url: $rootScope.apiConf.apiServer + '/permission/',
                method: 'GET',
                ignoreLoadingBar: false
            });
        };

        return {
            get: get
        };
    });
})();
