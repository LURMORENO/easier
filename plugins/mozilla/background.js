function onCreated() {
    if (browser.runtime.lastError) {
      console.log(`Error: ${browser.runtime.lastError}`);
    } else {
      console.log("Item created successfully");
    }
}

function onError(error) {
    console.log(`Error: ${error}`);
}

browser.contextMenus.create({
    id: "log-selection",
    title: "Easier",
    contexts: ["selection"]
}, onCreated);

function reportExecuteScriptError(error) {
  document.querySelector("#popup-content").classList.add("hidden");
  document.querySelector("#error-content").classList.remove("hidden");
  console.error(`Failed to execute content script: ${error.message}`);
}

browser.contextMenus.onClicked.addListener(function(info, tab) {
  function replace(tabs) {
    var xmlhttp = new XMLHttpRequest();
      xmlhttp.onreadystatechange = function(){
        if(this.readyState == 4 && this.status == 200){
          var result = JSON.parse(this.responseText)['result']
          var url = "https://easier.hulat.uc3m.es/api/synonyms-v2?"
          for (const sentencetags of result) {
            var xml = new XMLHttpRequest();
            xml.onreadystatechange = function(){
              if(this.readyState == 4 && this.status == 200){
                var synonym = JSON.parse(this.response)['result'][1]
                if (sentencetags[4]=="discapacidad"){
                        chrome.tabs.sendMessage(tabs[0].id, {
                          command: "replace",
                          tuple: { 
                            word:sentencetags[4],
                            synonym: "discapacidad"}
                })}
                else{
                chrome.tabs.sendMessage(tabs[0].id, {
                          command: "replace",
                          tuple: { 
                            word:sentencetags[4],
                            synonym: synonym}
					
				        })};
              }
            }
            xml.open("GET", url + `word=${sentencetags[4]}&sentencetags=${JSON.stringify(sentencetags)}`)
            xml.setRequestHeader("Content-Type", "application/json")
            xml.send()   
          }          
        }
      };
      var url = `https://easier.hulat.uc3m.es/api/complex-words?text=${info.selectionText}&flag=0`
      xmlhttp.open("GET", url, true)
      xmlhttp.setRequestHeader("Content-Type", "application/json")
      xmlhttp.send()      
  }

  function executeScript(){
    browser.tabs.query({active: true, currentWindow: true})
        .then(replace)
        .catch();
  }  
  
  if (info.menuItemId == "log-selection") {
    browser.tabs.insertCSS({file: 'content-style.css'});
    browser.tabs.executeScript({file: "replace.js"})
      .then(executeScript)
      .catch(reportExecuteScriptError);
    }
  });