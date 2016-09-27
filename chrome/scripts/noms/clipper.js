'use strict';

// root angular app
var app = angular.module("clipper", []);

var Clipper = app.controller("Clipper", ['$scope', '$http', function ($scope, $http) {
    var nomsbook = "http://localhost:8080/api/bookmarklet?uri=";
    $scope.saved = false; 
    $scope.showButton = true; 
    $scope.domainURL = "http://localhost:8080"

    // user clicked the save button 
    $scope.saveme = function() { 
        chrome.tabs.query({'active': true, 'lastFocusedWindow': true}, function (tabs) {
            $scope.url = tabs[0].url; 
            $http({method: 'GET', url: nomsbook + $scope.url}).then(function successCallback(response) { 
                $scope.message = "";

                var data = response['data'];  
                if (data['status'] === "error") {
                    $scope.message = 'statusError'; 
                    $scope.responseError = data['message']; 
                    $scope.showButton = false; 
                } 

                if (data['recipes'].length > 0) {
                    $scope.saved = true; 
                    $scope.showButton = false; 
                    $scope.recipes = data['recipes']; 
                }
            }, function errorCallback(response) { 
                // traceback occur on the server 404, 500 
                $scope.message = 'error'; 
                $scope.showButton = false; 
            }); 
        }); 
    }; 
}]);
