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
}, false);

// https://developer.chrome.com/extensions/overview