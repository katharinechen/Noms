'use strict';

// Karma configuration
// Generated on Wed Feb 12 2014 12:46:59 GMT-0800 (PST)

module.exports = function(config) {
  config.set({

    // base path, that will be used to resolve files and exclude
    basePath: '',
    frameworks: ['mocha', 'chai', 'sinon'],

    files: [
      // 'static/3p/angular.js',
      // 'static/3p/jquery.min.js',
      // 'static/3p/*.js',
      'noms/templates/application.html',
      'noms/templates/universal-header.html',
      'static/js/*.js',
      'static/js/controllers/*.js',
      'static/js/partials/*.html',
      'static/js/test/**/*.js',
    ],
    // list of files to exclude - please add a comment explaining why you added something here
    exclude: [],

    // possible values: 'dots', 'progress', 'junit', 'growl', 'coverage'
    reporters: ['mocha', 'coverage'],

    preprocessors: {
        'static/js/*.js': ['coverage'],
        'static/js/test/**/*.js': ['coverage'],
        },

    // // used by tests of directives that use partials, when you can't use an HTTP request to get the partial
    // ngHtml2JsPreprocessor: {
    //     moduleName: "partials"
    // },

    port: 9876,

    // enable / disable colors in the output (reporters and logs)
    colors: true,

    // possible values: config.LOG_DISABLE || config.LOG_ERROR || config.LOG_WARN || config.LOG_INFO || config.LOG_DEBUG
    logLevel: config.LOG_INFO,

    // enable / disable watching file and executing tests whenever any file changes
    autoWatch: false,

    browsers: ['ChromeHeadless'],

    // If browser does not capture in given timeout [ms], kill it
    captureTimeout: 60000,

    // if true, it capture browsers, run tests and exit
    singleRun: true
  });
};
