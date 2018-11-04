"use strict";

describe("static/js/controllers/recipe.js : Recipe", () => {
    var showStub = sinon.stub();
    beforeEach(module("noms"));

    // Replacing functions of $mdDialog with spies
    beforeEach(module(function ($provide) {
        $provide.decorator("$mdDialog", function($delegate) {
            $delegate.show = showStub.returns({
                then: function(cb) {
                    cb();
                }
            });
            return $delegate;
        });
    }));

    beforeEach(inject(($injector, $controller, $rootScope, $window) => {
        this.$httpBackend = $injector.get("$httpBackend");
        this.$mdDialog = $injector.get('$mdDialog');
        this.$q = $injector.get("$q");
        this.scope = $rootScope;
        $window.nomsPreload = "{\"urlKey\": \"yummy-food\"}";
        $window.onbeforeunload = () => 'Oh no!';
        $controller("Preload", {$scope: $rootScope, $window: $window});
        $controller("RecipeShow", {$scope: $rootScope});
    }));

    it("should read a recipe - success/failure", () => {
        var expected = {
            "name": "recipeee",
            "author": "mee",
            "user": "me@me.com",
            "urlKey": "yummy-food",
            "ingredients": [],
            "instructions": [],
            "recipeYield": "1 thing",
            "tags": [],
        };
        // readRecipe is called when the controller is initialized
        this.$httpBackend.expectGET("/api/recipe/yummy-food").respond(expected);
        this.$httpBackend.flush();
        expect(this.scope.recipe).to.deep.equal(expected);

        // using a wrong key
        expected = {}
        this.scope.readRecipe("wrong-key");
        this.$httpBackend.expectGET("/api/recipe/wrong-key").respond(403, expected);
        this.$httpBackend.flush();
        expect(this.scope.status).to.equal("Unable to read the recipe data: undefined");
    });

    it("should delete a recipe - success/failure", () => {
        this.$httpBackend.expectGET("/api/recipe/yummy-food").respond({});

        // calls the delete function
        this.scope.deleteRecipe("yummy-food");
        this.$httpBackend.expectPOST("/api/recipe/yummy-food/delete").respond({});
        this.$httpBackend.flush();

        // If error, provide apprropiate message
        this.scope.deleteRecipe("yummy-food");
        this.$httpBackend.expectPOST("/api/recipe/yummy-food/delete").respond(403, {});
        this.$httpBackend.flush();
        expect(this.scope.status).to.equal("Unable to delete customer data: undefined");
    });

    it("should show the showEditModal", () => {
        this.$httpBackend.expectGET("/api/recipe/yummy-food").respond({});
        this.scope.showEditModal({},{});
        sinon.assert.calledOnce(showStub);
    });

    it("should show the deleteConfirmModal", () => {
        this.$httpBackend.expectGET("/api/recipe/yummy-food").respond({});
        var deleteRecipe = sinon.spy(this.scope, "deleteRecipe");
        this.scope.deleteConfirm({},"yo");
        sinon.assert.calledOnce(deleteRecipe);
    });
});

describe("static/js/controllers/recipe.js : Recipe", () => {
    beforeEach(module("noms"));

    beforeEach(inject(($injector, $controller, $rootScope, $window) => {
        var dataToPass = {};
        this.$httpBackend = $injector.get("$httpBackend");
        this.$mdDialog = $injector.get('$mdDialog');
        this.scope = $rootScope;
        $window.nomsPreload = "{\"urlKey\": \"yummy-food\"}";
        $window.onbeforeunload = () => 'Oh no!';
        $controller("Preload", {$scope: $rootScope, $window: $window});
        $controller("DialogController", {$scope: $rootScope, dataToPass: dataToPass});

    }));

    it("should save a recipe - success/failure", () => {
        // success
        var saveAlert = sinon.spy(this.scope, "saveAlert");
        this.scope.saveRecipe({"urlKey": "yummy-food"});
        this.$httpBackend.expectPOST('/api/recipe/yummy-food/save').respond({});
        this.$httpBackend.flush();
        sinon.assert.calledOnce(saveAlert);

        // failure
        var errorAlert = sinon.spy(this.scope, 'errorAlert');
        this.scope.saveRecipe({"urlKey": "yummy-food"});
        this.$httpBackend.expectPOST('/api/recipe/yummy-food/save').respond(403, {});
        this.$httpBackend.flush();
        sinon.assert.calledOnce(errorAlert);
    });

    it("should cancel the dialog", () => {
        var cancel = sinon.spy(this.$mdDialog, "cancel");
        this.scope.cancel();
        sinon.assert.calledOnce(cancel);
    });
});

