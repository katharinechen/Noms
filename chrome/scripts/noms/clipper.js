'use strict';

// root angular app
var app = angular.module("clipper", []);

var Clipper = app.controller("Clipper", ['$scope', '$http', function ($scope, $http) {

    var nomsbook = "http://localhost:8080/api/bookmarklet?uri=";
    var checkPageButton = document.getElementById('checkPage');

    // put everything in an onclick
    chrome.tabs.query({'active': true, 'lastFocusedWindow': true}, function (tabs) {
        chrome.cookies.get({url: nomsbook, name: "TWISTED_SESSION"}, function(c) { 
            console.log(c);
            $scope.$apply(function(){ 
                $scope.url = tabs[0].url;  
                // can't get it sending cookies 
                $http({method: 'GET', url: nomsbook + $scope.url, headers: {cookie: c.name + "=" + c.value}}).then(function(recipes) {
                    $scope.recipes = recipes; 
                    $scope.welcomeMsg = recipes; 
                });
            });
        });
    });    
}]);