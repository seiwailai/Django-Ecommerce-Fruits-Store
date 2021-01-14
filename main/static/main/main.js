function initApplication(){
    initCarousel();
    initCartAdd();
    initCartUpdate();
    initHamburger();
}

document.onreadystatechange = function () {
    if (document.readyState === 'complete') {
      initApplication();
    }
  }