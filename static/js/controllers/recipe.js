'use strict';

// Controller for a single recipe
app.controller('RecipeShow', ['$scope', '$window', '$mdDialog', 'recipeFactory', function($scope, $window, $mdDialog, recipeFactory) {

    // Initalize Variables
    $scope.message = '';
    $scope.arraySections = ['tags', 'ingredients', 'instructions'];
    var urlKey = $scope.preload.urlKey;

    // Read
    $scope.readRecipe = function(urlKey) {
        recipeFactory.read(urlKey).then(
            (response) => {
                $scope.recipe = response.data;
            },
            (err) => {
                $scope.status = "Unable to read the recipe data: " + err.message;
            }
        );
    };
    $scope.readRecipe(urlKey);

    // Delete confirmation dialog
    $scope.deleteConfirm = function(ev, recipe) {
        var confirm = $mdDialog.confirm()
            .title('Would you like to delete this recipe?')
            .textContent('This is a permanent change. You will not be able to restore this recipe after delection.')
            .targetEvent(ev)
            .ok('Yes')
            .cancel('No');
        $mdDialog.show(confirm).then(function() {
            $scope.deleteRecipe(recipe.urlKey);
        });
    };

    // Delete a single recipe
    $scope.deleteRecipe = function(urlKey) {
        recipeFactory.delete(urlKey).then(
            () => {
                $window.location.href = '/recipes';
            },
            () => {
                $scope.status = "Unable to delete customer data";
            }
        );
    };

    // Show recipe edit modal
    $scope.showEditModal = function(ev, recipe) {
        $mdDialog.show({
            controller: 'DialogController',
            templateUrl: '/static/js/partials/recipe-update.html',
            parent: angular.element(document.body),
            targetEvent: ev,
            clickOutsideToClose: true,
            locals: {
                dataToPass: recipe
            },
        });
    };
}]);


app.controller('DialogController', ['$scope', '$mdDialog', 'recipeFactory', 'dataToPass', function($scope, $mdDialog, recipeFactory, dataToPass) {
    $scope.recipe = dataToPass;
    $scope.cancel = function() {
        $mdDialog.cancel();
    };

    // Update an existing recipe
    $scope.saveRecipe = function(modRecipe) {
        recipeFactory.update(modRecipe, modRecipe.urlKey).then(
            () => {
                $scope.saveAlert();
            },
            () => {
                $scope.errorAlert();
            }
        );
    };

    // Confirmation modal for saving a recipe
    $scope.saveAlert = function(ev){
        $mdDialog.show(
            $mdDialog.alert()
                .parent(angular.element(document.querySelector('#popupContainer')))
                .clickOutsideToClose(true)
                .title('Saved')
                .textContent('Your recipe was successfully saved. You did it!')
                .ok('Got it!')
                .targetEvent(ev)
        );
    };

    // Confirmation modal for saving a recipe
    $scope.errorAlert = function(ev){
        $mdDialog.show(
            $mdDialog.alert()
                .parent(angular.element(document.querySelector('#popupContainer')))
                .clickOutsideToClose(true)
                .title('Error')
                .textContent("There was an error with your save. Won't it have been awesome if we told you why?")
                .ok('You suck!')
                .targetEvent(ev)
        );
    };
}]);

