(function() {
    if (window.hasRun) {
      return;
    }
    window.hasRun = true;

    /**
 * Substituir palabras complejas por un tooltip y un sinonimo.
 *
 * @param  {Node} node    - Nodo del DOM.
 * @param {Tuple} tuple   - Tupla {palabra, sinonimo}
 * @return {void}         
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
     * Escucha los mensajes que le llegan del background script.
    */
   browser.runtime.onMessage.addListener((message) => {
      if (message.command === "replace") {
        replaceText(document.body, message.tuple)       

      } else if (message.command === "reset") {
        console.log("reset")
      }
    });
  
})(); 