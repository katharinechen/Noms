"use strict";

describe("static/js/controllers/recipe-list.js : RecipeListCtrl", () => {
    beforeEach(module("noms"));

    beforeEach(inject(($injector, $controller, $rootScope, $window, recipeFactory) => {
        this.$httpBackend = $injector.get("$httpBackend");
        this.scope = $rootScope;
        $window.nomsPreload = "{\"urlKey\": \"yummy-food\"}";
        $controller("Preload", {$scope: $rootScope, $window: $window, recipeFactory});
        $controller("RecipeListCtrl", {$scope: $rootScope, recipeFactory});
    }));

    it("should get a list - success", () => {
        // add something to the list
        var expected = [{
            "name": "recipeee",
            "author": "mee",
            "user": "me@me.com",
            "urlKey": "yummy-food",
            "ingredients": [],
            "instructions": [],
            "recipeYield": "1 thing",
            "tags": [],
        }];
        // success
        this.scope.showList();
        this.$httpBackend.expectGET("api/recipe/list").respond(expected);
        this.$httpBackend.flush();
        expect(this.scope.recipes).to.deep.equal(expected);
    });

    it("should get a list - fail", () => {
        // add something to the list
        var expected = {
            err: "oh no"
        };
        // failure
        this.scope.showList();
        this.$httpBackend.expectGET("api/recipe/list").respond(403, expected);
        this.$httpBackend.flush();
        expect(this.scope.status).to.equal("Unable to load customer data: undefined");
    });
});
