'use strict';

/**
 *
 * Main module of the application.
 */
(function () {
    var app = angular.module('proctor', [
        'ngRoute',
        'ngCookies',
        'ngAnimate',
        'ngSanitize',
        'ngTable',
        'ui.bootstrap',
        'checklist-model',
        'proctor.i18n',
        'proctor.api',
        'proctor.session',
        'proctor.date',
        'websocket',
        'pascalprecht.translate',
        'tokenAuth'
    ]);
    app.config(function ($routeProvider,
                         $controllerProvider,
                         $locationProvider,
                         $compileProvider,
                         $filterProvider,
                         $provide,
                         $httpProvider,
                         $translateProvider,
                         $translateLocalStorageProvider,
                         $interpolateProvider) {

        // Redefine angular entities for lazy loading feature
        app.controller = $controllerProvider.register;
        app.directive = $compileProvider.directive;
        app.routeProvider = $routeProvider;
        app.filter = $filterProvider.register;
        app.service = $provide.service;
        app.factory = $provide.factory;

        app.path = window.app.rootPath;
        app.language = {
            // current: (window.localStorage['NG_TRANSLATE_LANG_KEY'] !== undefined && window.localStorage['NG_TRANSLATE_LANG_KEY']) ? window.localStorage['NG_TRANSLATE_LANG_KEY'] : 'en',
            current: window.app.spaConfig.language,
            supported: ['en', 'ru']
        };

        $locationProvider.html5Mode(true);

        delete $httpProvider.defaults.headers.common['X-Requested-With'];

        $interpolateProvider.startSymbol('{[');
        $interpolateProvider.endSymbol(']}');

        // I18N
        $translateProvider.useStaticFilesLoader({
            prefix: app.path + 'i18n/',
            suffix: '.json'
        });
        $translateProvider.preferredLanguage(app.language.current);
        $translateProvider.useSanitizeValueStrategy('sanitize');
        $translateProvider.useLocalStorage();

        // Decorators for modals and popups
        // Redefine bootstrap ui templates
        $provide.decorator('uibModalBackdropDirective', function ($delegate) {
            $delegate[0].templateUrl = app.path + 'ui/partials/modal/backdrop.html';
            return $delegate;
        });
        $provide.decorator('uibModalWindowDirective', function ($delegate) {
            $delegate[0].templateUrl = app.path + 'ui/partials/modal/window.html';
            return $delegate;
        });
        $provide.decorator('uibTooltipPopupDirective', function ($delegate) {
            $delegate[0].templateUrl = app.path + 'ui/partials/tooltip/tooltip-popup.html';
            return $delegate;
        });

        $routeProvider
            .when('/', {
                templateUrl: app.path + 'ui/home/view.html',
                controller: 'MainCtrl',
                resolve: {
                    deps: function (resolver, Auth, $q, $location) {
                        var deferred = $q.defer();
                        Auth.is_proctor().then(function (is) {
                            if (is) {
                                resolver.load_deps([
                                    app.path + 'ui/home/hmController.js',
                                    app.path + 'ui/home/hmDirectives.js',
                                    app.path + 'common/services/exam_polling.js',
                                    app.path + 'common/services/ws_data.js'
                                ], function(){
                                    deferred.resolve();
                                });
                            } else {
                                $location.path('/archive');
                                deferred.resolve();
                            }
                        });
                        return deferred.promise;
                    },
                    students: function ($location, TestSession, Api) {
                        if (window.sessionStorage['proctoring'] !== undefined) {
                            TestSession.setSession(
                                JSON.parse(window.sessionStorage['proctoring'])
                            );
                        }
                        var session = TestSession.getSession();
                        if (!session) {
                            $location.path('/session');
                            return true;
                        } else {
                            var ret = Api.restore_session();
                            if (ret == undefined) {
                                $location.path('/session');
                                return true;
                            }
                            else {
                                return ret;
                            }
                        }
                    }
                }
            })
            .when('/session', {
                templateUrl: app.path + 'ui/sessions/view.html',
                controller: 'SessionCtrl',
                resolve: {
                    deps: function ($location, resolver, Auth) {
                        var ret = resolver.load_deps([
                            app.path + 'ui/sessions/rsController.js',
                            app.path + 'ui/sessions/rsDirectives.js'
                        ]);
                        return Auth.is_proctor().then(function (is) {
                            if (is) {
                                return ret;
                            } else {
                                $location.path('/archive');
                            }
                        }, function(err) {
                            $location.path('/index');
                            return { resolveError : err }
                        });
                    },
                    data: function (Api) {
                        return Api.get_session_data();
                    }
                }
            })
            .when('/session/:hash', {
                controller: 'MainController',
                resolve: {
                    deps: function ($location, TestSession, $q, $route, Auth) {
                        var deferred = $q.defer();
                        Auth.is_instructor().then(function (is) {
                            if (is) {
                                $location.path('/archive');
                            } else {
                                TestSession.fetchSession($route.current.params.hash)
                                .then(function(){
                                    deferred.resolve();
                                    $location.path('/');
                                }, function(reason) {
                                    if(reason.status == 403){
                                        $location.path('/archive');
                                    }
                                });
                            }
                        });
                        return deferred.promise;
                    }
                }
            })
            .when('/archive', {
                templateUrl: app.path + 'ui/archive/view.html',
                controller: 'ArchCtrl',
                resolve: {
                    deps: function (resolver) {
                        return resolver.load_deps([
                            app.path + 'ui/archive/archController.js',
                            app.path + 'common/modules/date.js'
                        ]);
                    },
                    events: function (Api, $location) {
                        return Api.get_archived_events().then(function(response) {
                            return response;
                        }, function(err) {
                            console.error(err);
                            $location.path('/index');
                            return { resolveError : err }
                        });
                    },
                    courses_data: function (Api, $location) {
                        return Api.get_session_data().then(function(response) {
                            return response
                        }, function(err) {
                            console.error(err);
                            $location.path('/index');
                            return { resolveError : err }
                        });
                    }
                }
            })
            .when('/archive/:hash', {
                templateUrl: app.path + 'ui/archive/sessions_view.html',
                controller: 'ArchAttCtrl',
                resolve: {
                    deps: function (resolver) {
                        return resolver.load_deps([
                            app.path + 'ui/archive/archAttController.js'
                        ]);
                    },
                    sessions: function ($route, Api) {
                        return Api.get_archived_sessions($route.current.params.hash).then(function(response) {
                            return response
                        }, function(err) {
                            console.error(err);
                            return { resolveError: err }
                        });
                    }
                }
            })
            .when('/profile', {
                templateUrl: app.path + 'ui/profile/view.html',
                controller: 'ProfileCtrl',
                resolve: {
                    deps: function (resolver) {
                        return resolver.load_deps([
                            app.path + 'ui/profile/pfController.js'
                        ]);
                    },
                    me: function (Auth) {
                        return true;
                    }
                }
            })
            .when('/index', {
                template: '<div>Error</div>',
                controller : 'errControler'
            })
            .otherwise({
                redirectTo: '/'
            });
    });

    app.run(['$rootScope', '$location', '$translate', function ($rootScope, $location, $translate) {
        var domain;
        var match = $location.absUrl().match(/(?:https?:\/\/)?(?:www\.)?(.*?)\//);
        if (match !== null)
            domain = match[1];
        var api_port = '', socket_port = '';
        var protocol = 'http://';
        if ("https:" == document.location.protocol) {
            protocol = 'https://';
        }
        $rootScope.apiConf = {
            domain: domain,
            protocol: protocol,
            ioServer: domain + (socket_port ? ':' + socket_port : ''),
            apiServer: protocol + domain + (api_port ? ':' + api_port : '') + '/api'
        };

        // Preload language files
        // Use only if `allow_language_change` is true
        //angular.forEach(app.language.supported, function (val) {
        //    if (val !== app.language.current) {
        //        $translate.use(val);
        //    }
        //});
    }]);

    // Lazy loading feature for angular 1.x
    app.factory('resolver', function ($rootScope, $q, $timeout, $location, Auth) {
        return {
            load_deps: function (dependencies, callback) {
                // Preload resources only if authenticated
                if (Auth.authenticate()) {
                    var deferred = $q.defer();
                    $script(dependencies, function () {
                        $timeout(function () {
                            $rootScope.$apply(function () {
                                deferred.resolve();
                                if (callback !== undefined)
                                    callback();
                            });
                        });
                    });
                    return deferred.promise;
                } else {
                    $location.path('/');
                }
            }
        };
    });

    // MAIN CONTROLLER
    app.controller('MainController', ['$scope', '$translate', '$http', 'i18n', 'TestSession',
        function ($scope, $translate, $http, i18n, TestSession) {

            var lng_is_supported = function (val) {
                return app.language.supported.indexOf(val) >= 0 ? true : false;
            };

            $scope.get_supported_languages = function () {
                return app.language.supported;
            };

            $scope.changeLanguage = function (langKey) {
                if (langKey == undefined) langKey = app.language.current;
                if (lng_is_supported(langKey)) {
                    $translate.use(langKey);
                    i18n.clear_cache();
                    app.language.current = langKey;
                }
            };

            $scope.sso_auth = function () {
                window.location = window.app.loginUrl;
            };

            $scope.logout = function () {
                TestSession.flush();
                window.location = window.app.logoutUrl;
            };

            $scope.i18n = function (text) {
                return i18n.translate(text);
            };

            //$scope.changeLanguage();
        }]);

    app.controller('HeaderController', ['$scope', '$location', function ($scope, $location) {
        $scope.session = function () {
            $location.path('/session');
        };
    }]);

    app.directive('header', [function () {
        return {
            restrict: 'E',
            templateUrl: app.path + 'ui/partials/header.html',
            link: function (scope, e, attr) {
            }
        };
    }]);
})();
