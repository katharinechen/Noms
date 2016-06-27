'use strict';

// root angular app
var app = angular.module("clipper", []);

var Clipper = app.controller("Clipper", ['$scope', '$http', function ($scope, $http) {
    var nomsbook = "http://localhost:8080/api/bookmarklet?uri=";
    $scope.message = "Please press button!"
    $scope.saved = false; 

    // user clicked the save button 
    $scope.saveme = function() { 
        chrome.tabs.query({'active': true, 'lastFocusedWindow': true}, function (tabs) {
            $scope.url = tabs[0].url; 
            $http({method: 'GET', url: nomsbook + $scope.url}).then(function successCallback(response) { 
                $scope.message = "";

                var data = response['data'];  
                if (data['status'] === "error") {
                    $scope.message = $scope.message + data['message']; 
                } 

                if (data['recipes'].length > 0) {
                    $scope.saved = true; 
                    $scope.recipes = data['recipes']; 
                    $scope.message = $scope.message + " We saved the following recipes:"; 
                }
            }, function errorCallback(response) { 
                // traceback occur on the server 404, 500 
                $scope.message = "We are not not able to save your recipe at this time. Sorry!"
            }); 
        }); 
    }; 
}]);
