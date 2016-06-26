'use strict';

// root angular app
var app = angular.module("clipper", []);

var Clipper = app.controller("Clipper", ['$scope', '$http', function ($scope, $http) {
    var nomsbook = "http://localhost:8080/api/bookmarklet?uri=";
    $scope.message = "Please press button!"

    // user clicked the save button 
    $scope.saveme = function() { 
        // find the active tab and get the url 
        chrome.tabs.query({'active': true, 'lastFocusedWindow': true}, function (tabs) {
            $scope.url = tabs[0].url; 
  
            // make a http request to bookmarklet 
            $http({method: 'GET', url: nomsbook + $scope.url}).then(function successCallback(response) { 
                var data = response['data'];                 
                if (data === "Error") { 
                    $scope.message = "We are not able to save your recipe at this time. Sorry!"
                } else { 
                    $scope.message = "We saved the following recipes: " + data.join(", ")
                }

            }, function errorCallback(response) { 
                // called asynchronously if an error occus or server returns response with an error status 
                console.log(response);
                console.log("server gave me an error"); 
            }); 
        }); 
    }; 
}]);
