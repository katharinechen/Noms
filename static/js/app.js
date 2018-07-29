'use strict';

// root angular app
var app = angular.module("noms", ["ngMaterial", "ngMessages"]);

app.controller("Preload", ['$rootScope', '$window', function ($rootScope, $window) {
    // the nomsPreload object on the window is used by jinja templates to pass
    // server-side data to the angular app
    if ($window.nomsPreload) {
        $rootScope.preload = JSON.parse($window.nomsPreload);
    }
}]);

app.config(function($mdThemingProvider){
    $mdThemingProvider.theme('docs-dark');
});
