'use strict'; 

// controls the display of a single recipe
app.controller('Recipe', ['$scope', '$http', '$location', function($scope, $http, $location) {
    // FIXME! What happens if it is not the last argument? :(
    var fullUrl = $location.absUrl(); 
    var urlKey = fullUrl.split("/"); 
    urlKey = urlKey[urlKey.length - 1]; 

    $http({method: 'GET', url: '/api/recipe/' + urlKey}).then(function(recipe) {
        $scope.recipe = recipe.data; 
    }); 
}]); 

