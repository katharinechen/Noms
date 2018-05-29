'use strict';

// root angular app
var app = angular.module("noms", ["xeditable", "ngTagsInput", "ngMaterial", "ngMessages"]);

app.run(function(editableOptions) {
    editableOptions.theme = 'default'; // bootstrap3 theme. Can be also 'bs2', 'default'
});

app.controller("Preload", ['$rootScope', '$window', function ($rootScope, $window) {
    // the nomsPreload object on the window is used by jinja templates to pass
    // server-side data to the angular app
    if ($window.nomsPreload) {
        $rootScope.preload = JSON.parse($window.nomsPreload);
    }
}]);