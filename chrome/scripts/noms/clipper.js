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
                console.log(response['data']); 
                var recipes = response['data'];  
                // not sure we need this... 
                if (recipes === "Error") {
                    $scope.saved = false;  
                    $scope.message = "We are not able to save your recipe at this time. Sorry!"
                } else { 
                    // need to send back the url keys (link = nomsbook + urlKey)
                    $scope.saved = true; 
                    $scope.recipes = recipes; 
                    $scope.message = "We saved the following recipes: " 
                }
            }, function errorCallback(response) { 
                console.log(response);
                $scope.message = "We are not not able to save your recipe at this time. Sorry!"
            }); 
        }); 
    }; 
}]);
