loading_spinner = new XMLHttpRequest();
loading_spinner.open("GET","static/index/svg/spinner.svg",false);
// Following line is just to be on the safe side;
// not needed if your server delivers SVG with correct MIME type
loading_spinner.overrideMimeType("image/svg+xml");
loading_spinner.send("");
