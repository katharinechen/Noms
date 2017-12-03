'use strict';

// controls the list of recipes
app.controller('NewRecipeCtrl', ['$scope', '$http', '$mdDialog', '$mdToast', function($scope, $http,  $mdDialog, $mdToast) {
    $scope.recipe = {};

    $scope.saveNewRecipe = function(recipe) {
      recipe = Object.assign({}, recipe);
      recipe.ingredients = [recipe.ingredients];
      recipe.instructions = [recipe.instructions];

      $http.post('/api/recipe/create', recipe).success(function(data) {
        $scope.ok = true;
        if (data.status === "error") {
            $scope.errorAlert(data.message); 
        } else {
            // when it is successfully, need to send the user to the right link 
            // when applicable 
            $scope.saveAlert(); 
        }
      }).error(function (err) {
        $scope.errorAlert(err); 
      });
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
          .ok('You suck!')
      );
  };
}]);
