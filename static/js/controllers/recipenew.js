"use strict";

// controls the list of recipes
app.controller('NewRecipeCtrl', ['$scope', '$http', '$mdDialog', '$mdToast', '$window', function($scope, $http,  $mdDialog, $mdToast, $window) {
    $scope.recipe = {};

    // ingredients and instructions are entered in large textboxes
    // items could be seperated by either commas or newlines
    // insert all items into an array
    $scope.parseTextBox = function(content) {
        return content.split(/[\n,]+/);
    };

    $scope.saveNewRecipe = function(recipe) {
        recipe = Object.assign({}, recipe);

        recipe.ingredients = $scope.parseTextBox(recipe.ingredients);
        recipe.instructions = $scope.parseTextBox(recipe.instructions);
        recipe.tags = $scope.parseTextBox(recipe.tags);

        $http.post('/api/recipe/create', recipe).then(
            (response) => {
                var data = response.data;
                // when it is successfully, need to send the user to the right link
                // when applicable
                $scope.saveAlert();
                $window.location.href = '/recipes/' + data.message;
            },
            (err) => {
                if (err.status === 403) {
                    $scope.errorAlert('In order to save your recipe, you must log in to Noms first!');
                } else {
                    $scope.errorAlert(err.data);
                }
            }
        );
    };

    // Confirmation modal for saving a recipe
    $scope.saveAlert = function(){
        $mdDialog.show(
            $mdDialog.alert()
                .parent(angular.element(document.querySelector('#popupContainer')))
                .clickOutsideToClose(true)
                .title('Saved')
                .textContent('Your recipe was successfully saved. You did it!')
                .ok('Got it!')
        );
    };

    // Confirmation modal for saving a recipe
    $scope.errorAlert = function(err){
        $mdDialog.show(
            $mdDialog.alert()
                .parent(angular.element(document.querySelector('#popupContainer')))
                .clickOutsideToClose(true)
                .title('Error')
                .textContent(err)
                .ok('Ok')
        );
    };
}]);