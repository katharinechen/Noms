'use strict';

// root angular app
var app = angular.module("noms", []);

var Noms = app.controller("Noms", ['$scope', '$window', function ($scope, $window) {
    // the nomsPreload object on the window is used by jinja templates to pass
    // server-side data to the angular app
    if ($window.nomsPreload) {
        $scope.preload = JSON.parse($window.nomsPreload);
    }
}]);
