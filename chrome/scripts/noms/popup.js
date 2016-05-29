// DOMCOntentLoaded = this event is fired when the initial HTML document has been completely loaded and parsed 
document.addEventListener('DOMContentLoaded', function() {
    
    var url = ""; 
    var nomsbook = "http://localhost:8080/api/bookmarklet?uri=";
    var checkPageButton = document.getElementById('checkPage');

    // save the url for the current page 
    chrome.tabs.query({'active': true, 'lastFocusedWindow': true}, function (tabs) {
            url = tabs[0].url;
        });    

    // send bookmarklet the link of the recipe link
    openTab = function() { 
        chrome.tabs.create({url: nomsbook +  encodeURIComponent(url)});
    }; 
    checkPageButton.addEventListener('click', openTab, false);

    // check for http.response? 


    // chrome.webRequest.onCompleted.addListener(function(response){ 
    //         return {}
    //     }); 



    //  chrome.webRequest.onBeforeRequest.addListener(
    //     function(details) {
    //       return {cancel: details.url.indexOf("://www.evil.com/") != -1};
    //     },
    //     {urls: ["<all_urls>"]},
    //     ["blocking"]);
      


}, false);

// https://developer.chrome.com/extensions/overview
// https://developer.chrome.com/apps/angular_framework (also talks about Auth0)
// https://gist.github.com/jjperezaguinaga/4243341 (Awesome docs explaining the architecture)