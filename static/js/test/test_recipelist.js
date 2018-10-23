"use strict";

describe("static/js/controllers/recipe-list.js : RecipeListCtrl", () => {
    beforeEach(module("noms"));

    beforeEach(inject(($injector, $controller, $rootScope) => {
        this.$httpBackend = $injector.get("$httpBackend");
        this.scope = $rootScope;
        $controller("RecipeListCtrl", {$scope: $rootScope});
    }));

    it("should get a list", () => {
        var expected = [{
            "name": "recipeee",
            "author": "mee",
            "user": "me@me.com",
            "urlKey": "/me-recipeee",
            "ingredients": [],
            "instructions": [],
            "recipeYield": "1 thing",
            "tags": [],
        }];
        this.$httpBackend.expectGET("/api/recipe/list").respond(expected);
        this.$httpBackend.flush();
        expect(this.scope.recipes).to.deep.equal(expected);
    });
});
