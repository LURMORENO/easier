document.addEventListener("click", (e) => {
    if (e.target.classList.contains("easier")) {
      if(e.target.textContent == '¿Qué es?'){
        browser.tabs.create({
          url: "http://163.117.129.208:8080/project"
        });
      }
      else{
        browser.tabs.create({
          url: "http://163.117.129.208:8080/download"
        })
      }
    }
  });