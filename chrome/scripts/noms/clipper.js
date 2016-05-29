'use strict';

// root angular app
var app = angular.module("clipper", []);

var Clipper = app.controller("Clipper", ['$scope', function ($scope) {
    $scope.welcomeMsg = "This is your first chrome extension";
}]);





// angular.module('clipper')
//   .controller('MainController', ['$scope', function($scope) {
//       $scope.welcomeMsg = "This is your first chrome extension";

//       // $scope.contribute = function() {
//       //   chrome.tabs.create({
//       //     url: 'https://github.com/flrent/chrome-extension-angular-base'
//       //   })
//       // }
//   }])
// ;
