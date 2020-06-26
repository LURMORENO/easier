function onCreated() {
    if (chrome.runtime.lastError) {
      console.log(`Error: ${chrome.runtime.lastError}`);
    } else {
      console.log("Item created successfully");
    }
}

function onError(error) {
    console.log(`Error: ${error}`);
}

chrome.contextMenus.create({
    id: "log-selection",
    title: "Easier",
    contexts: ["selection"]
}, onCreated);

function reportExecuteScriptError(error) {
  document.querySelector("#popup-content").classList.add("hidden");
  document.querySelector("#error-content").classList.remove("hidden");
  console.error(`Failed to execute beastify content script: ${error.message}`);
}


chrome.contextMenus.onClicked.addListener(function(info, tab) {

  function replace(tabs) {
    var xmlhttp = new XMLHttpRequest();
      xmlhttp.onreadystatechange = function(){
        if(this.readyState == 4 && this.status == 200){
          var result = JSON.parse(this.responseText)
          var b = JSON.parse(result.result)

          chrome.tabs.sendMessage(tabs[0].id, {
            command: "beastify",
            result: b
          });
          
        }

      };

      var prod = "http://163.117.129.208:8000/easierapp/api/result?original_text="
      // var deb = "http://127.0.0.1:8000/easierapp/api/result?original_text="
      
      xmlhttp.open("GET", prod+info.selectionText, true)
      xmlhttp.setRequestHeader("Content-Type", "application/json")
      xmlhttp.send()
      
  }

  function executeScript(){
    chrome.tabs.query({active: true, currentWindow: true}, replace)
        // .then(replace)
        // .catch();
  
  }  
  
  
  if (info.menuItemId == "log-selection") {
    chrome.tabs.insertCSS({file: 'content-style.css'});
    chrome.tabs.executeScript({file: "replace.js"}, executeScript)
      // .then(executeScript)
      // .catch(reportExecuteScriptError);
    }
  });

function openPage() {
  chrome.tabs.create({
    url: "http://163.117.129.208:8000/easierapp/"
  });
}

chrome.browserAction.onClicked.addListener(openPage);