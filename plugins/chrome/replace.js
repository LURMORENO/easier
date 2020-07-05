(function() {
  if (window.hasRun) {
    return;
  }
  window.hasRun = true;

  /**
* Substitutes emojis into text nodes.
* If the node contains more than just text (ex: it has child nodes),
* call replaceText() on each of its children.
*
* @param  {Node} node    - The target DOM Node.
* @return {void}         - Note: the emoji substitution is done inline.
*/
function replaceText (node, tuple) {
if (node.nodeType === Node.TEXT_NODE) {
  if (node.parentNode &&
      node.parentNode.nodeName === 'TEXTAREA') {
    return;
  }
  if(node.parentElement.nodeName === 'P'){
    let content = node.parentElement.innerHTML;
    let regex = new RegExp(`\\b${tuple.word}\\b`, 'i');
    content = content.replace(regex, `<div class=tooltip>${tuple.word} <span class=tooltiptext>${tuple.synonym}</span></div>`);
    node.parentElement.innerHTML = content;
  }
}
else {
  for (let i = 0; i < node.childNodes.length; i++) {
    replaceText(node.childNodes[i], tuple);
  }    
}
}

  /**
   * Listen for messages from the background script.
   * Call "beastify()" or "reset()".
  */
 chrome.runtime.onMessage.addListener((message) => {
    if (message.command === "replace") {
      replaceText(document.body, message.tuple)       

    } else if (message.command === "reset") {
      console.log("reset")
    }
  });

})(); 