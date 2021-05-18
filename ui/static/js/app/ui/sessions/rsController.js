(function () {
    angular.module('proctor').controller('SessionCtrl', function ($scope, $location, data, TestSession,
                                                                  DateTimeService, i18n, $uibModal, Api) {
        $scope.orgs = [];
        $scope.orgDetails = [];
        $scope.courses = [];
        $scope.courses_titles = [];
        $scope.runs = [];
        $scope.exams = [];
        $scope.chosenOrg = null;
        $scope.chosenCourse = null;
        $scope.chosenCourseTitle = null;
        $scope.chosenRun = null;
        $scope.chosenExam = null;
        $scope.testingCentre = '';
        $scope.startSessionInProgress = false;
        $scope.errorMsg = '';
        $scope.archGridOptions = {
            data: [],
            sort: {
                predicate: 'id',
                direction: 'desc'
            }
        };
        $scope.currentActiveSession = null;

        function checkProctoredExams(v) {
            return v.proctored_exams.length && (v.has_access === true);
        }

        function sortArr(key) {
            return function(a, b) {
                if (a[key] < b[key]) return -1;
                if (a[key] > b[key]) return 1;
                return 0;
            };
        }

        var sortOrgsArr = sortArr('name');
        var sortRunsArr = sortArr('run');
        var sortExamsArr = sortArr('exam_name');

        $scope.updateCourses = function() {
            var courses = [];
            var courses_titles = [];

            angular.forEach(data.data.results, function (val) {
                if ((val.org === $scope.chosenOrg.key) && (courses.indexOf(val.id) === -1)
                    && checkProctoredExams(val)) {
                    courses.push(val.id);
                    courses_titles.push(val.course_title);
                }
            });
            //courses.sort();
            $scope.courses = courses;
            $scope.courses_titles = courses_titles;

            if ($scope.courses.length > 0) {
                $scope.chosenCourse = $scope.courses[0];
                $scope.chosenCourseTitle = $scope.courses_titles[0];
            }

            $scope.updateRuns();
        };

        $scope.updateRuns = function() {
            var runs = [];
            angular.forEach(data.data.results, function (val) {
                if ((val.org === $scope.chosenOrg.key) && (val.course_title === $scope.chosenCourseTitle)
                    && (runs.indexOf(val.run) === -1) && checkProctoredExams(val)) {
                    runs.push(val);
                }
            });
            //runs.sort(sortRunsArr);
            $scope.runs = runs;
            //for (key in runs) {
            //    console.log('key '+key);
            //}

            if ($scope.runs.length > 0) {
                $scope.chosenRun = $scope.runs[0];
            }

            $scope.updateSessions();
        };

        $scope.updateSessions = function () {
            var runs = [];
            angular.forEach(data.data.results, function (val) {
                if ((val.org === $scope.chosenOrg.key) && (val.course_title === $scope.chosenCourseTitle) &&
                    (val.course_session === $scope.chosenRun.course_session) && (runs.indexOf(val.run) === -1) && checkProctoredExams(val)) {
                    $scope.exams = [];
                    angular.forEach(val.proctored_exams, function (proctored_exam) {
                        $scope.exams.push({
                            id: proctored_exam.id,
                            exam_name: proctored_exam.exam_name,
                            exam_name_short: (proctored_exam.exam_name.length > 60) ? (proctored_exam.exam_name.substr(0, 60) + '...') : proctored_exam.exam_name
                        })
                    });
                    $scope.exams.sort(sortExamsArr);
                    $scope.chosenExam = $scope.exams[0];
                }
            });
            $scope.errorMsg = '';
        };

        $scope.showSessionCreateError = function (exam) {
            $uibModal.open({
                animation: true,
                templateUrl: "sessionCreateError.html",
                controller: 'SessionErrorCtrl',
                size: 'lg',
                resolve: {
                    exam: exam
                }
            });
        };

        $scope.startSession = function () {
            $scope.startSessionInProgress = true;
            $scope.errorMsg = '';
            TestSession.registerSession($scope.testingCentre, $scope.chosenRun.id, $scope.chosenExam.id,
                $scope.chosenRun.name, $scope.chosenExam.exam_name, function() {
                    $scope.errorMsg = i18n.translate('SESSION_ERROR_1');
                    $scope.startSessionInProgress = false;
                }).then(function (data) {
                    if (data) {
                        if (data.created) {
                            $location.path('/session/' + data.exam.hash_key);
                        } else {
                            $scope.startSessionInProgress = false;
                            $scope.showSessionCreateError(data.exam);
                        }
                    } else {
                        $scope.startSessionInProgress = false;
                    }
            }, function () {});
        };

        function getArchData() {
            Api.get_archived_events(5).then(function(response) {
                $scope.archGridOptions.data = getArchGridData(response.data.results, i18n);
            }, function(err) {

            });
        }

        if (data.data.results !== undefined && data.data.results.length) {
            var orgs = [];
            var orgDetails = [];
            angular.forEach(data.data.results, function (val) {
                if ((orgs.indexOf(val.org) === -1) && checkProctoredExams(val)) {
                    orgs.push(val.org);
                    orgDetails.push({
                        name: val.org_description,
                        key: val.org
                    })
                }
            });
            orgs.sort();
            orgDetails.sort(sortOrgsArr);
            $scope.orgs = orgs;
            $scope.orgDetails = orgDetails;

            if ($scope.orgDetails.length > 0) {
                $scope.chosenOrg = $scope.orgDetails[0];
                $scope.updateCourses();
            }
        }

        if (data.data.current_active_sessions !== undefined && data.data.current_active_sessions.length) {
            $scope.currentActiveSession = data.data.current_active_sessions[0];
        }

        $scope.gotoSession = function(hash_key) {
            window.location.href = window.location.origin + '/session/' + hash_key;
        };

        getArchData();
    });

    angular.module('proctor').controller('SessionErrorCtrl', function ($scope, $uibModalInstance, DateTimeService,
                                                                       i18n, exam) {
        $scope.exam = exam;
        $scope.examLink = window.location.origin + '/session/' + exam.hash_key;

        $scope.ok = function () {
            $uibModalInstance.close();
            window.location.href = $scope.examLink;
        };

        $scope.close = function () {
            $uibModalInstance.close();
        };

        $scope.i18n = function (text) {
            return i18n.translate(text);
        };
    });
})();
