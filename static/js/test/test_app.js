"use strict";


describe("static/js/controllers/app.js : Preload", () => {
    beforeEach(module("noms"));

    beforeEach(inject(($controller, $rootScope, $window) => {
        this.scope = $rootScope;
        this.window_ = $window;
        this.$controller = $controller;
    }));

    it("should use the value of nomsPreload", () => {
        this.window.nomsPreload = '{"hello": "world"}';
        expect(this.scope.preload).to.be.undefined;
        this.$controller('Preload', {
            $scope: this.scope, $window: this.window_
        });
        expect(this.scope.preload.hello).to.equal("world");
    });
});
